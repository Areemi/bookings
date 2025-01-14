from pydantic import EmailStr
from app.tasks.celery import celery
from PIL import Image
from pathlib import Path
import smtplib

from app.tasks.email_templates import create_booking_confirmation_template
from app.config import settings


@celery.task
def process_picture(
path: str,
):
    im_path = Path(path)
    im = Image.open(im_path)
    for width, height in [
        (1000, 500),
        (200, 100)
    ]:
        resized_img = im.resize(size=(width, height))
        resized_img.save(f"app/static/images/resized_{width}_{height}_{im_path.name}")
    

@celery.task
def send_booking_confirmation_email(
    booking: dict,
    email_to: EmailStr
):
    #email_to = settings.SMTP_USER
    msg_content = create_booking_confirmation_template(booking, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)