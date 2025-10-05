from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta

# Reportlab PDF uchun
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

import os
import openai
import json
from django.views.decorators.csrf import csrf_exempt

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

openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_page(request):
    return render(request, "chatbot.html")

@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Разрешены только POST-запросы."}, status=405)

    if not openai.api_key:
        return JsonResponse({"error": "API-ключ не найден. Обратитесь к администратору."}, status=500)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Пустое сообщение."}, status=400)

        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — медицинский помощник для людей с диабетом. "
                        "Отвечай КРАТКО и ЯСНО "
                        "Избегай лишних объяснений, если не требуется."
                    )
                },
                {"role": "user", "content": user_message},
            ],
            max_tokens=2000,
            temperature=1,
        )

        reply = resp["choices"][0]["message"]["content"].strip()
        return JsonResponse({"reply": reply})

    except openai.error.OpenAIError as oe:
        return JsonResponse({"error": f"Ошибка OpenAI: {str(oe)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)
    # -------------------------------------------------------------------
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.utils import timezone
from datetime import timedelta
from .models import Entry

# ✅ Unicode shriftni ulaymiz (Linux /usr/share/fonts/truetype/dejavu/ ichida bor)
pdfmetrics.registerFont(TTFont('LiberationSans', '/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf'))

@login_required
def export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="diary_report.pdf"'

    # PDF hujjat
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()

    # Maxsus stillar
    styles.add(ParagraphStyle(name="TitleCenter", fontName="LiberationSans", fontSize=16, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name="NormalText", fontName="LiberationSans", fontSize=12, spaceAfter=12))
    styles.add(ParagraphStyle(name="Footer", fontName="LiberationSans", fontSize=9, textColor=colors.grey, alignment=2))

    elements = []

    # Sarlavha
    elements.append(Paragraph(" Отчёт за последние 28 дней", styles["TitleCenter"]))
    elements.append(Paragraph(f" Пользователь: {request.user.username}", styles["NormalText"]))
    elements.append(Spacer(1, 12))

    # So‘nggi 28 kunlik yozuvlarni olish
    entries = Entry.objects.filter(
        user=request.user,
        datetime__gte=timezone.now() - timedelta(days=28)
    ).order_by("-datetime")

    # Jadval sarlavhasi
    data = [["Дата", "Рост (см)", "Вес (кг)", "Глюкоза (ммоль/л)"]]

    # Jadval qatorlari
    for e in entries:
        data.append([
            e.datetime.strftime("%d.%m.%Y %H:%M"),
            str(e.height) if e.height else "-",
            str(e.weight) if e.weight else "-",
            str(e.glucose) if e.glucose else "-"
        ])

    # Jadval yaratamiz
    table = Table(data, colWidths=[120, 100, 100, 120])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'LiberationSans'),
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

    # Footer
    elements.append(Paragraph("Отчёт сгенерирован автоматически системой HealD", styles["Footer"]))

    # PDFni yig‘amiz
    doc.build(elements)
    return response


# -------------------------------------------------------------------
# Index sahifasi
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
            if user is not None:
                login(request, user)
            try:
                _ = user.userprofile
                return redirect('dashboard')
            except UserProfile.DoesNotExist:
                return redirect('profile_setup')
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


# -------------------------------------------------------------------
# Dashboard sahifasi
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
# Qo‘shimcha yozuv qo‘shish
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
    try:
        profile = request.user.userprofile
        return redirect('dashboard')
    except UserProfile.DoesNotExist:
        profile = None

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
# Mashqlar sahifasi
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

        medicine = Medicine.objects.create(
            user=request.user,
            name=name,
            dose=dose,
        )

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
# Bildirishnomalar (push log)
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
