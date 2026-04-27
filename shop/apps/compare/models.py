from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class CompareItem(models.Model):
    session_key = models.CharField("Ключ сесії", max_length=40, blank=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name="compare_items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="compared_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Порівняння"
        verbose_name_plural = "Порівняння"

    def __str__(self) -> str:
        return f"Порівняння: {self.product.name}"
