from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from .utils import normalize_phone


class UserManager(BaseUserManager):
    
    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        phone_number = normalize_phone(phone_number)
        if not phone_number:
            raise ValueError('Phone number is required')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)   # hashes it  never stored in plain text
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    username = None   # remove the username column entirely

    phone_number = models.CharField(
        max_length=15,
        unique=True,   # the login identifier — must be unique
        # Arabic digits are converted to ASCII (normalize_phone) before this
        # validator runs — \d matches ASCII digits after normalization.
        validators=[RegexValidator(r'^\+?\d{8,15}$',
                                   'Enter a valid phone number, e.g. +9665XXXXXXXX')],
    )

    USERNAME_FIELD = "phone_number"   # what login (and simplejwt) authenticates with
    REQUIRED_FIELDS = []              # createsuperuser asks only phone + password

    objects = UserManager()

    def save(self, *args, **kwargs):
        # for  every save (admin edits, direct .save(), etc.)
        self.phone_number = normalize_phone(self.phone_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number
