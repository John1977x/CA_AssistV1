import smtplib
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings


def _send_email(to_email: str, subject: str, html_body: str):
    if not settings.SMTP_USER:
        print(f"[EMAIL - SMTP not configured] To: {to_email} | Subject: {subject}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())


async def _send_email_async(to_email: str, subject: str, html_body: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_email, to_email, subject, html_body)


async def send_welcome_email(to_email: str, name: str, firm_name: str):
    subject = f"Welcome to CA Assists — {firm_name}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f8fafc;border-radius:12px;">
      <h2 style="color:#1e40af;">Welcome to CA Assists, {name}!</h2>
      <p>Your firm <strong>{firm_name}</strong> is now set up on CA Assists.</p>
      <p>You have a <strong>14-day free trial</strong> with full access to all features.</p>
      <a href="{settings.FRONTEND_URL}/login" style="display:inline-block;background:#1e40af;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;margin-top:16px;">Login to CA Assists</a>
      <p style="color:#64748b;margin-top:24px;font-size:13px;">If you have questions, reply to this email anytime.</p>
    </div>
    """
    await _send_email_async(to_email, subject, html)


async def send_invite_email(to_email: str, to_name: str, firm_name: str, token: str):
    link = f"{settings.FRONTEND_URL}/accept-invite?token={token}"
    subject = f"You're invited to join {firm_name} on CA Assists"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f8fafc;border-radius:12px;">
      <h2 style="color:#1e40af;">You're Invited!</h2>
      <p>Hi {to_name},</p>
      <p><strong>{firm_name}</strong> has invited you to join their workspace on CA Assists.</p>
      <a href="{link}" style="display:inline-block;background:#1e40af;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;margin-top:16px;">Accept Invitation</a>
      <p style="color:#64748b;margin-top:16px;font-size:13px;">This link expires in 48 hours.</p>
    </div>
    """
    await _send_email_async(to_email, subject, html)


async def send_reset_password_email(to_email: str, name: str, token: str):
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "Reset your CA Assists password"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f8fafc;border-radius:12px;">
      <h2 style="color:#1e40af;">Reset Password</h2>
      <p>Hi {name},</p>
      <p>Click the button below to reset your password. This link is valid for 2 hours.</p>
      <a href="{link}" style="display:inline-block;background:#dc2626;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;margin-top:16px;">Reset Password</a>
      <p style="color:#64748b;margin-top:16px;font-size:13px;">If you didn't request this, ignore this email.</p>
    </div>
    """
    await _send_email_async(to_email, subject, html)
