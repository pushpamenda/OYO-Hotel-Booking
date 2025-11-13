from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('verify-accounts/<str:token>/', views.verify_email_token, name='verify_email_token'),
]
