from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import MedicineTime
from .utils import send_sms


def check_medicine_times():
    now = timezone.localtime().time().replace(second=0, microsecond=0)
    medicines = MedicineTime.objects.filter(time__hour=now.hour, time__minute=now.minute)

    for med_time in medicines:
        medicine = med_time.medicine
        user = medicine.user
        profile = getattr(user, "userprofile", None)

        if profile and profile.phone:
            message = f"{medicine.name} dorisini {medicine.dose} miqdorda ichish vaqti bo‘ldi."
            send_sms(profile.phone, message)
            print(f"✅ SMS yuborildi: {profile.phone} → {message}")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_medicine_times, "interval", minutes=1)
    scheduler.start()
    print("📅 Dori tekshiruvchi scheduler ishga tushdi.")
