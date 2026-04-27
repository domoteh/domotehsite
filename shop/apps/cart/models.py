from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class CartItem(models.Model):
    session_key = models.CharField("Ключ сесії", max_length=40, blank=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField("Кількість", default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Елемент кошика"
        verbose_name_plural = "Елементи кошика"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=models.Q(user__isnull=False),
                name="unique_user_product",
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"],
                condition=models.Q(session_key__gt=""),
                name="unique_session_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.product.retail_price * self.quantity
