from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from .utils import sanitize_html


class SiteSettings(models.Model):
    phone_1 = models.CharField("Телефон 1", max_length=20, blank=True)
    phone_2 = models.CharField("Телефон 2", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    shop_name = models.CharField("Назва магазину", max_length=255, default="DOMOTEH")
    shop_tagline = models.CharField("Слоган", max_length=255, default="Інтернет-магазин низьких цін")

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self) -> str:
        return "Налаштування сайту"

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class StaticPage(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", unique=True, allow_unicode=True)
    content = CKEditor5Field("Контент", config_name="default")
    is_active = models.BooleanField("Активна", default=True)
    sort_order = models.IntegerField("Порядок", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Статична сторінка"
        verbose_name_plural = "Статичні сторінки"
        ordering = ["sort_order"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        self.content = sanitize_html(self.content)
        super().save(*args, **kwargs)


class NewsletterSubscriber(models.Model):
    email = models.EmailField("Email", unique=True)
    is_active = models.BooleanField("Активний", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Підписник"
        verbose_name_plural = "Підписники"

    def __str__(self) -> str:
        return self.email
