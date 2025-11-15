from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('send_otp/<email>/' , views.send_otp, name='send_otp'),
    path('verify_otp/<email>/' , views.verify_otp, name='verify_otp'),
    path('login_vendor/' , views.login_vendor, name='login_vendor'),
    path('register_vendor/' , views.register_vendor, name='register_vendor'),
    path('vendor_dashboard/', views.vendor_dashboard, name="vendor_dashboard"),
    path('add_hotels/',views.add_hotels,name="add_hotels"),
    path('<slug>upload_images/', views.upload_images,name="upload_images"),
    path('delete_image/<int:id>/', views.delete_image, name='delete_image'),
    path('edit_hotel/<slug>/',views.edit_hotel , name = "edit_hotel"),
    path('logout/' , views.logout_view , name="logout_view"),
    path('verify-accounts/<str:token>/', views.verify_email_token, name='verify_email_token'),
]
