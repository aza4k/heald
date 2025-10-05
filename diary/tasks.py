from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.conf import settings
from diary.models import MedicineTime
import requests

def send_sms(phone, message):
    """Eskiz API orqali SMS yuborish"""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjIxOTU5MjAsImlhdCI6MTc1OTYwMzkyMCwicm9sZSI6InRlc3QiLCJzaWduIjoiYTYyZTk1ZjNiYmE3YjM3Y2M0MDJlYTI1NzNiMjYyNWMzYjEzZWNmMWZjOWFjMGQ3MDgzYjQzMWM1NjNkYzlmOCIsInN1YiI6IjEyNzg2In0.yxRfDXwvkdY8iOHzh9_rH6BEoH8c17h0KaN7LSCxaic"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "mobile_phone": phone,
        "message": message,
        "from": "4546"  # Eskiz’da berilgan kod
    }

    res = requests.post("https://notify.eskiz.uz/api/message/sms/send", json=data, headers=headers)
    print("SMS status:", res.status_code, res.text)


def check_and_send_medicine_sms():
    """Har daqiqa foydalanuvchilarning dorilarini tekshiradi va vaqt keldi deb topsa — SMS yuboradi."""
    now = timezone.localtime().time().replace(second=0, microsecond=0)
    current_time = now.strftime("%H:%M")

    meds = MedicineTime.objects.filter(time__hour=now.hour, time__minute=now.minute)
    for mt in meds:
        user = mt.medicine.user
        profile = getattr(user, "userprofile", None)
        if profile and profile.phone:
            text = f"⏰ Время принять лекарство: {mt.medicine.name} ({mt.medicine.dose})"
            send_sms(profile.phone, text)
            print(f"SMS отправлено пользователю {profile.phone}: {text}")
        else:
            print(f"❌ У пользователя {user.username} нет профиля или номера телефона")


def start_scheduler():
    """Django ishga tushganda fon scheduler’ni ishga tushiradi."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_medicine_sms, "interval", minutes=1)
    scheduler.start()
