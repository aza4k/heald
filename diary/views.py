from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GlucoseEntry
from .forms import GlucoseEntryForm
import matplotlib.pyplot as plt
import io, base64
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ro‘yxatdan o‘tganidan keyin avtomatik login qiladi
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


@login_required
def dashboard(request):
    entries = GlucoseEntry.objects.filter(user=request.user).order_by('-created_at')[:20]

    # Grafik
    values = [e.value for e in entries][::-1]
    dates = [e.created_at.strftime("%d-%m %H:%M") for e in entries][::-1]

    chart = None
    if values:
        fig, ax = plt.subplots()
        ax.plot(dates, values, marker="o")
        ax.set_ylabel("Glyukoza (mmol/L)")
        ax.set_title("Oxirgi natijalar")
        plt.xticks(rotation=45)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        buf.seek(0)
        chart = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

    return render(request, "dashboard.html", {"entries": entries, "chart": chart})

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
