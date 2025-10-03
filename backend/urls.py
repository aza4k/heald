from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('diary.urls')),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    ]
