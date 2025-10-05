from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_entry, name='add_entry'),
    path('register/', views.register, name='register'),
    path('profile-setup/', views.profile_setup, name='profile_setup'),  # agar profile_setup funksiyangiz bo'lsa
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('exercises/', views.exercises_view, name='exercises'),
    path("medicines/", views.medicines_view, name="medicines"),
    path('delete/<int:med_id>/', views.delete_medicine, name='delete_medicine'),
    path('chat/', views.chat_page, name='chatbot_page'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path("notifications/", views.notifications_view, name="notifications"),
    path("diet/", views.diet_view, name="diet"),
    ]
