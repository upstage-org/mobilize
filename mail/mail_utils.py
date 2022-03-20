from multiprocessing import Process
from email.mime.text import MIMEText
from smtplib import (
    SMTP_SSL as SMTP,)  # this invokes the secure SMTP protocol (port 465, uses SSL)
import sys
import os
import re

from config.settings import (EMAIL_HOST, EMAIL_PORT,
    EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS,
    ADMIN_EMAIL, ENV_TYPE)

def send_sync(to, subject, content):

    msg = MIMEText(content, "html")
    msg["Subject"] = f'{ENV_TYPE}: {subject}'
    # some SMTP servers will do this automatically, not all
    msg["From"] = EMAIL_HOST_USER
    msg["Bcc"] = to + f' {ADMIN_EMAIL}'

    # Always use TLS.
    conn = SMTP(EMAIL_HOST, EMAIL_PORT)
    conn.set_debuglevel(False)
    conn.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    try:
        recipients = re.split(r'[,;]\s*', to)
        conn.sendmail(EMAIL_HOST_USER, recipients, msg.as_string())
    finally:
        conn.quit()

def send(to, subject, content):
    Process(target=send_sync, args=(to, subject, content)).start()
