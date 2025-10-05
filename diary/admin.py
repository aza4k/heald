from django.contrib import admin
from .models import UserProfile, Medicine, MedicineTime, GlucoseEntry, Entry

admin.site.register(UserProfile)
admin.site.register(Medicine)
admin.site.register(MedicineTime)
admin.site.register(GlucoseEntry)
admin.site.register(Entry)
