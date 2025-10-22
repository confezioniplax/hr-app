# app/services/email_sender.py
from __future__ import annotations
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from ..settings import get_settings  # come in db.py

class EmailSender:
    def __init__(self):
        s = get_settings()
        self.host = getattr(s, "SMTP_HOST", None)
        self.port = int(getattr(s, "SMTP_PORT", 587))
        self.user = getattr(s, "SMTP_USER", None)
        self.password = getattr(s, "SMTP_PASSWORD", None)
        self.sender_name = getattr(s, "SMTP_SENDER_NAME", "PLAX Notifiche")
        self.sender_email = getattr(s, "SMTP_FROM", self.user)
        self.use_tls = bool(getattr(s, "SMTP_TLS", True))

    def send_html(self, *, to: list[str], subject: str, html: str):
        if not self.host or not self.sender_email:
            raise RuntimeError("SMTP non configurato correttamente")
        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = formataddr((self.sender_name, self.sender_email))
        msg["To"] = ", ".join(to)

        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            if self.user and self.password:
                server.login(self.user, self.password)
            server.sendmail(self.sender_email, to, msg.as_string())
