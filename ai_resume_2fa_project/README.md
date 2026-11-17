# AI Resume Parser & Multi-Channel 2FA Pipeline

## 1. Install
Use Python 3.11 or newer. Create a virtual environment:

Windows:
    py -m venv venv
    venv\Scripts\activate

macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate

Install packages:
    pip install -r requirements.txt

## 2. PostgreSQL
Create a database named `resume_app` in PostgreSQL.
Copy `.env.example` to `.env` and update DATABASE_URL with your PostgreSQL password.
Keep JWT_SECRET private.

## 3. Run
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs to test APIs.

## 4. API order
1. POST /api/v1/resume/parse (multipart form; field name: file)
2. POST /api/v1/auth/register (JSON)
3. POST /api/v1/auth/send-2fa?email=...&channel=email
4. Read the development OTP in the terminal (or your configured email inbox).
5. POST /api/v1/auth/verify-2fa (JSON)
6. GET /api/v1/profile?email=...
7. PATCH /api/v1/profile?email=...
8. GET /dashboard/student

Register JSON example:
{
  "name": "Arun Kumar",
  "email": "arun@example.com",
  "phone": "9876543210",
  "password": "StrongPass123",
  "skills": ["python", "sql"],
  "experience": "Fresher",
  "qualification": "BSc Computer Science"
}

Verify JSON example:
{
  "email": "arun@example.com",
  "code": "123456",
  "channel": "email"
}

## Important learning/demo notes
- Resume extraction is rule-based starter parsing, not a trained AI model. Users must review extracted data.
- Email sends for real only after SMTP settings are configured.
- WhatsApp is a provider integration placeholder; it prints a development code and does not send a WhatsApp message.
- Browser TOTP verification works only after a TOTP secret has been securely enrolled. This starter accepts a secret at registration for demonstration; a production app must generate and confirm it through a separate enrollment flow and show a QR code.
- Profile endpoints currently identify the user by email for easy local learning. A production app must verify the JWT and derive the user identity from the token; never trust a client-supplied email for authorization.
- Add rate limits, OTP attempt limits, secure secret storage, migrations (Alembic), HTTPS, and proper JWT authorization before production use.
