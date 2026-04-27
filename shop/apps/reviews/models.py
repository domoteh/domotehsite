from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField("Оцінка", choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField("Текст відгуку")
    is_approved = models.BooleanField("Схвалений", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        unique_together = [("product", "user")]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Відгук {self.user} на {self.product.name}"


class Question(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="questions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField("Питання")
    answer = models.TextField("Відповідь", blank=True)
    is_answered = models.BooleanField("Відповіді дано", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Питання"
        verbose_name_plural = "Питання"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Питання від {self.user} — {self.product.name}"
