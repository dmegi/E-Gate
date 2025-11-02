from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from datetime import date, timedelta


# ✅ Fix for expiry_date (lambdas cannot be serialized in migrations)
def default_expiry_date():
    return date.today() + timedelta(days=365)


class User(AbstractUser):
    is_resident = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


class ResidentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    barangay_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    address = models.CharField(max_length=255)
    birthdate = models.DateField()
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    date_registered = models.DateField(default=date.today)
    expiry_date = models.DateField(default=default_expiry_date)

    def __str__(self):
        return f"{self.user.username} - {self.barangay_id}"
