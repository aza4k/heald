from django.db import models
from django.contrib.auth.models import User

class GlucoseEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField()  # mmol/L
    note = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.value} mmol/L ({self.created_at})"
