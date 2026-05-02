import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os

import logging

logging.basicConfig(level=logging.INFO)

SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "a9f8bd001@smtp-brevo.com"
SMTP_PASSWORD = "5g1DOLEUS3ZcmTJI"

FROM_EMAIL = "julian.kergosien@insa-rennes.fr"

DESTINATAIRE_TEST = "julian.kergosien.dhn@gmail.com"

HEURE_CIBLE = datetime.now().strftime("%H:%M")

def envoyer_mail_test():
 
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = DESTINATAIRE_TEST
    msg["Subject"] = "Le test fonctionne !"

    msg.attach(MIMEText("Ceci signifie que cela fonctionne correctement", "plain"))

    server.sendmail(FROM_EMAIL, DESTINATAIRE_TEST, msg.as_string())
    server.quit()

def envoyer_mails_programmes():
    now = datetime.now().strftime("%H:%M")
    print(f"[CHECK] maintenant = {now}, cible = {HEURE_CIBLE}")

    if now >= HEURE_CIBLE:
        print("[SEND] envoi du mail")
        envoyer_mail_test()

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            envoyer_mails_programmes,
            "interval",
            minutes=1,
            max_instances=1,
            coalesce=True
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    start_scheduler()

    import time
    while True:
        time.sleep(1)
