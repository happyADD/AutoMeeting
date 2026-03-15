"""Email service tests (content and mock SMTP)."""
from unittest.mock import patch, MagicMock
import pytest
from app.services.email import send_appointment_email


def test_send_appointment_email_skips_when_smtp_not_configured():
    with patch("app.services.email.get_settings") as m:
        m.return_value = MagicMock(
            smtp_host="",
            smtp_user="",
            smtp_password="",
            smtp_from_email="noreply@test.com",
            smtp_port=587,
            smtp_use_tls=True,
        )
        # Should not raise
        send_appointment_email(
            to_email="counselor@test.com",
            counselor_name="张老师",
            appointment_date="2025-03-15",
            period="morning",
            hour=9,
            content="学业咨询",
            contact_name="小明",
            contact_phone="13800138000",
            contact_email="x@test.com",
        )


def test_send_appointment_email_calls_smtp_when_configured():
    with patch("app.services.email.get_settings") as m_settings:
        m_settings.return_value = MagicMock(
            smtp_host="smtp.test.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="pass",
            smtp_from_email="from@test.com",
            smtp_use_tls=True,
        )
        with patch("app.services.email.smtplib.SMTP") as m_smtp:
            send_appointment_email(
                to_email="counselor@test.com",
                counselor_name="李老师",
                appointment_date="2025-03-16",
                period="afternoon",
                hour=14,
                content="心理辅导",
                contact_name="小红",
                contact_phone=None,
                contact_email="hong@test.com",
            )
            m_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()
            call_args = m_smtp.return_value.__enter__.return_value.sendmail.call_args
            assert call_args[0][1] == ["counselor@test.com"]
            body = call_args[0][2]
            assert "2025-03-16" in body
            assert "下午" in body
            assert "14" in body
            assert "心理辅导" in body
            assert "小红" in body
            assert "hong@test.com" in body
