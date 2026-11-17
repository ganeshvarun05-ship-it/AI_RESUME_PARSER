from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import pyotp

from app.database import engine, get_db
from app.models import Base, User, Resume, OTPChallenge
from app.schemas import RegisterRequest, VerifyOTPRequest, ProfileUpdate
from app.parser import extract_text, parse_resume
from app.security import hash_password, make_otp, hash_otp, create_access_token
from app.config import OTP_EXPIRE_MINUTES
from app.services.otp import send_email_otp, send_whatsapp_otp

app = FastAPI(title="AI Resume Parser & 2FA Pipeline")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def home():
    return {"message": "Resume Parser API is running", "docs": "/docs"}

@app.post("/api/v1/resume/parse")
async def parse_resume_api(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "Upload a PDF or DOCX file")
    content = await file.read()
    try:
        raw_text = extract_text(file.filename, content)
    except Exception as exc:
        raise HTTPException(400, f"Could not read resume: {exc}")
    data = parse_resume(raw_text)
    db.add(Resume(email=data["email"], filename=file.filename, extracted_text=raw_text))
    await db.commit()
    return {"extracted": data, "message": "Check and edit these details before registration"}

@app.post("/api/v1/auth/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(409, "Email is already registered")
    user = User(
        name=payload.name, email=payload.email, phone=payload.phone,
        password_hash=hash_password(payload.password),
        skills=", ".join(payload.skills), experience=payload.experience,
        qualification=payload.qualification, totp_secret=payload.totp_secret,
        is_active=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"message": "Registration staged. Verify an OTP to activate the account."}

@app.post("/api/v1/auth/send-2fa")
async def send_2fa(email: str, channel: str = "email", db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(404, "User not found")
    if channel not in ("email", "whatsapp"):
        raise HTTPException(400, "For browser TOTP, use the verify endpoint with channel=totp")
    code = make_otp()
    challenge = OTPChallenge(
        email=email, otp_hash=hash_otp(code), channel=channel,
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    )
    db.add(challenge)
    await db.commit()
    if channel == "email":
        send_email_otp(email, code)
    else:
        if not user.phone:
            raise HTTPException(400, "Add a phone number before WhatsApp verification")
        send_whatsapp_otp(user.phone, code)
    return {"message": f"{channel} verification started"}

@app.post("/api/v1/auth/verify-2fa")
async def verify_2fa(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user:
        raise HTTPException(404, "User not found")

    if payload.channel == "totp":
        if not user.totp_secret:
            raise HTTPException(400, "TOTP is not configured for this account")
        valid = pyotp.TOTP(user.totp_secret).verify(payload.code, valid_window=1)
    else:
        result = await db.execute(
            select(OTPChallenge).where(
                OTPChallenge.email == payload.email,
                OTPChallenge.channel == payload.channel,
                OTPChallenge.used == False
            ).order_by(OTPChallenge.id.desc())
        )
        challenge = result.scalars().first()
        valid = bool(
            challenge and challenge.expires_at > datetime.utcnow()
            and challenge.otp_hash == hash_otp(payload.code)
        )
        if valid:
            challenge.used = True

    if not valid:
        raise HTTPException(400, "Invalid or expired verification code")
    user.is_active = True
    await db.commit()
    return {"access_token": create_access_token(user.email), "token_type": "bearer",
            "redirect_url": "/dashboard/student"}

@app.get("/api/v1/profile")
async def get_profile(email: str, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == email))
    if not user or not user.is_active:
        raise HTTPException(401, "Active user not found")
    return {"name": user.name, "email": user.email, "phone": user.phone,
            "skills": (user.skills or "").split(", ") if user.skills else [],
            "experience": user.experience, "qualification": user.qualification}

@app.patch("/api/v1/profile")
async def update_profile(email: str, payload: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == email))
    if not user or not user.is_active:
        raise HTTPException(401, "Active user not found")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "skills" and value is not None:
            value = ", ".join(value)
        setattr(user, key, value)
    await db.commit()
    return {"message": "Profile updated"}

@app.get("/dashboard/student")
async def student_dashboard():
    return {"page": "Student Dashboard", "status": "You are ready to continue"}
