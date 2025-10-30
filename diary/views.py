from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt

import os
import json
import openai

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from .models import (
    GlucoseEntry,
    UserProfile,
    Entry,
    Medicine,
    MedicineTime,
    NotificationLog,
)
from .forms import (
    GlucoseEntryForm,
    UserProfileForm,
    EntryForm,
    MedicineForm,
)

# -------------------------------------------------------------------
# 🔑 OpenAI sozlamalari (GPT-5)
openai.api_key = "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"

# -------------------------------------------------------------------
# 🧠 Chat sahifasi
def chat_page(request):
    return render(request, "chatbot.html")


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Faqat POST so‘rovlariga ruxsat berilgan."}, status=405)
    
    if not openai.api_key:
        return JsonResponse({"error": "API-ключ topilmadi."}, status=500)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Bo‘sh xabar."}, status=400)

        # ✅ GPT-5 javobi (nanoda)
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Siz diabet bilan og‘rigan foydalanuvchilarga yordam beruvchi tibbiy yordamchisiz. "
                        "Javoblaringiz qisqa, aniq va foydali bo‘lsin."
                    )
                },
                {"role": "user", "content": user_message},
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        reply = resp["choices"][0]["message"]["content"].strip()
        return JsonResponse({"reply": reply})
    except openai.error.OpenAIError as oe:
        return JsonResponse({"error": f"OpenAI xatosi: {str(oe)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Server xatosi: {str(e)}"}, status=500)


# -------------------------------------------------------------------
# ✅ PDF eksport funksiyasi (standart Helvetica shrift bilan)
@login_required
def export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="diary_report.pdf"'

    # PDF hujjat
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()

    # Maxsus stillar (Helvetica — standart shrift)
    styles.add(ParagraphStyle(name="TitleCenter", fontName="Helvetica-Bold", fontSize=16, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name="NormalText", fontName="Helvetica", fontSize=12, spaceAfter=12))
    styles.add(ParagraphStyle(name="Footer", fontName="Helvetica", fontSize=9, textColor=colors.grey, alignment=2))

    elements = []

    # Sarlavha
    elements.append(Paragraph("Отчёт за последние 28 дней", styles["TitleCenter"]))
    elements.append(Paragraph(f"Пользователь: {request.user.username}", styles["NormalText"]))
    elements.append(Spacer(1, 12))

    # So‘nggi 28 kunlik yozuvlarni olish
    entries = Entry.objects.filter(
        user=request.user,
        datetime__gte=timezone.now() - timedelta(days=28)
    ).order_by("-datetime")

    data = [["Дата", "Рост (см)", "Вес (кг)", "Глюкоза (ммоль/л)"]]

    for e in entries:
        data.append([
            e.datetime.strftime("%d.%m.%Y %H:%M"),
            str(e.height) if e.height else "-",
            str(e.weight) if e.weight else "-",
            str(e.glucose) if e.glucose else "-"
        ])

    # Jadval
    table = Table(data, colWidths=[120, 100, 100, 120])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Отчёт сгенерирован автоматически системой HealD", styles["Footer"]))

    # PDFni yaratish
    doc.build(elements)
    return response

# -------------------------------------------------------------------
# Index
def index(request):
    latest = None
    if request.user.is_authenticated:
        latest = GlucoseEntry.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, "index.html", {"latest": latest})

# -------------------------------------------------------------------
# Ro‘yxatdan o‘tish
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            if user:
                login(request, user)
            try:
                _ = user.userprofile
                return redirect('dashboard')
            except UserProfile.DoesNotExist:
                return redirect('profile_setup')
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

# -------------------------------------------------------------------
# Dashboard
@login_required
def dashboard(request):
    userhealth = Entry.objects.filter(user=request.user).order_by('-datetime').first()

    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            if not entry.datetime:
                entry.datetime = timezone.now()
            entry.save()
            return redirect('dashboard')
    else:
        form = EntryForm()

    entries = Entry.objects.filter(user=request.user).order_by('datetime')
    dates = [e.datetime.strftime("%d.%m %H:%M") for e in entries]
    glucose_values = [e.glucose for e in entries]
    height_values = [e.height for e in entries]
    weight_values = [e.weight for e in entries]

    return render(request, 'dashboard.html', {
        'form': form,
        'userhealth': userhealth,
        'entries': entries,
        'dates': dates,
        'glucose_values': glucose_values,
        'height_values': height_values,
        'weight_values': weight_values,
    })

# -------------------------------------------------------------------
# Qo‘shimcha yozuv
@login_required
def add_entry(request):
    if request.method == "POST":
        form = GlucoseEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect("dashboard")
    else:
        form = GlucoseEntryForm()
    return render(request, "add_entry.html", {"form": form})

# -------------------------------------------------------------------
# Profil sozlamalari
@login_required
def profile_setup(request):
    if hasattr(request.user, 'userprofile'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            new_profile = form.save(commit=False)
            new_profile.user = request.user
            new_profile.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm()

    return render(request, 'profile_setup.html', {'form': form})

# -------------------------------------------------------------------
def exercises_view(request):
    return render(request, "exercises.html")

# -------------------------------------------------------------------
# Dori-darmonlar
@login_required
def medicines_view(request):
    medicines = Medicine.objects.filter(user=request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        dose = request.POST.get("dose")
        times = request.POST.getlist("times[]")

        medicine = Medicine.objects.create(user=request.user, name=name, dose=dose)
        for t in times:
            if t:
                MedicineTime.objects.create(medicine=medicine, time=t)

        return redirect("medicines")

    return render(request, "medicines.html", {"medicines": medicines})

@login_required
def delete_medicine(request, med_id):
    medicine = get_object_or_404(Medicine, id=med_id, user=request.user)
    medicine.delete()
    return redirect("medicines")

# -------------------------------------------------------------------
@login_required
def notifications_view(request):
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    times = MedicineTime.objects.filter(medicine__user=request.user)

    for t in times:
        exists = NotificationLog.objects.filter(
            user=request.user,
            medicine=t.medicine,
            time=t.time,
            date=today
        ).exists()

        if current_time >= t.time and not exists:
            NotificationLog.objects.create(
                user=request.user,
                medicine=t.medicine,
                time=t.time,
                date=today
            )

    logs = NotificationLog.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notifications.html", {"logs": logs})

# -------------------------------------------------------------------
@login_required
def diet_view(request):
    return render(request, "diet.html")

def unread_notifications(request):
    if request.user.is_authenticated:
        today = timezone.now().date()
        count = NotificationLog.objects.filter(
            user=request.user,
            date=today,
            is_taken=False
        ).count()
        return {"unread_notifications_count": count}
    return {"unread_notifications_count": 0}
