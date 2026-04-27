from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField("Телефон", max_length=20, blank=True)
    company_name = models.CharField("Назва компанії", max_length=255, blank=True)
    is_wholesale = models.BooleanField("Гуртовий клієнт", default=False)

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self) -> str:
        return self.get_full_name() or self.username
