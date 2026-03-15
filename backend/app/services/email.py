"""Send appointment notification email to counselor via SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings


def send_appointment_email(
    to_email: str,
    counselor_name: str,
    appointment_date: str,
    period: str,
    hour: int,
    content: str,
    contact_name: str,
    contact_phone: str | None,
    contact_email: str | None,
) -> None:
    """Send one email to the counselor. Raises on SMTP failure."""
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user:
        # Skip sending if SMTP not configured (e.g. dev)
        return

    period_cn = "上午" if period == "morning" else "下午"
    body = f"""
您有一条新的谈话预约通知。

预约时间：{appointment_date} {period_cn} {hour}:00
谈话内容/主题：{content}
联系人：{contact_name}
联系电话：{contact_phone or '未填写'}
联系邮箱：{contact_email or '未填写'}

请及时处理。
    """.strip()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"【谈话预约】{appointment_date} {period_cn} {hour}:00 - {contact_name}"
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_user and settings.smtp_password:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.sendmail(settings.smtp_from_email, [to_email], msg.as_string())
