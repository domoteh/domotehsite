from django.db import models


class StaticPage(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", unique=True, allow_unicode=True)
    content = models.TextField("Контент")
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


class NewsletterSubscriber(models.Model):
    email = models.EmailField("Email", unique=True)
    is_active = models.BooleanField("Активний", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Підписник"
        verbose_name_plural = "Підписники"

    def __str__(self) -> str:
        return self.email
