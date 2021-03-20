from django.urls import path
from . import views


urlpatterns = [
    path('user/signup/', views.register, name='register'),
    path('signup_success/', views.signup_success, name='signup_success'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('user/login/', views.login_view, name="login_view"),
    path('my_profile/view/', views.my_profile, name='my_profile'),
    path('add/address/', views.add_address, name='add_address'),
    path('edit/address/<str:pk>/', views.edit_address, name='edit_address'),
    path('update/personal-information/', views.personal_information, name='personal_information'),
    path('become-vendor/', views.become_vendor, name="become_vendor"),
    path('seller/registration/', views.seller_register, name="seller_register"),
    path('seller/login/', views.seller_login_view, name="seller_login_view"),
    path('seller/dashboard/', views.vendor_dashboard, name="vendor_dashboard"),
]