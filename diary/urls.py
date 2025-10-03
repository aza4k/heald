from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('add/', views.add_entry, name="add_entry"),
    path('register/', views.register, name="register"),
]
