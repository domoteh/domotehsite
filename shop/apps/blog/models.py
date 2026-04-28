from django.conf import settings
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from .utils import sanitize_html


class BlogPost(models.Model):
    class PostType(models.TextChoices):
        ARTICLE = "article", "Стаття"
        PROMO = "promo", "Акція"
        VIDEO = "video", "Відеоогляд"
        NEWS = "news", "Новина"

    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", unique=True, allow_unicode=True)
    post_type = models.CharField("Тип", max_length=20, choices=PostType.choices, default=PostType.ARTICLE)
    content = CKEditor5Field("Контент", config_name="default")
    image = models.ImageField("Зображення", upload_to="blog/", blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_published = models.BooleanField("Опубліковано", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Публікація"
        verbose_name_plural = "Публікації"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("blog:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs) -> None:
        self.content = sanitize_html(self.content)
        super().save(*args, **kwargs)
