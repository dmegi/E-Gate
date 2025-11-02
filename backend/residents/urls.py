from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_resident, name='register_resident'),
    path('login/', views.login_resident, name='login_resident'),
    path('profile/', views.resident_profile, name='resident_profile'),
    path('virtual-id/', views.resident_virtual_id, name='resident_virtual_id'),
]
