from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField("ФИО", max_length=255)
    birth_date = models.DateField("Дата рождения",blank=True, null=True)
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    address = models.CharField("Адрес проживания", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.full_name


class GlucoseEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField()  # mmol/L
    note = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.value} mmol/L ({self.created_at})"


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now)
    glucose = models.FloatField()
    height = models.FloatField()
    weight = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.datetime.strftime('%Y-%m-%d %H:%M')}"


class Medicine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dose = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.dose})"


class MedicineTime(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="times")
    time = models.TimeField()  # Har kuni shu vaqtda
    last_sent = models.DateField(blank=True, null=True)  # Qachon yuborilganini saqlaydi

    def __str__(self):
        return f"{self.medicine.name} - {self.time}"

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            birth_date=timezone.now().date(),  # vaqtinchalik bugungi sana
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class NotificationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    is_taken = models.BooleanField(default=False)  # yangi maydon

    def __str__(self):
        return f"{self.medicine.name} - {self.date} {self.time}"
