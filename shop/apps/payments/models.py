from django.db import models

from apps.orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Очікує"
        SUCCESS = "success", "Успішно"
        FAILED = "failed", "Помилка"
        REFUNDED = "refunded", "Повернено"

    class Provider(models.TextChoices):
        MONOBANK = "monobank", "MonoBank"
        COD = "cod", "Накладений платіж"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField("Провайдер", max_length=20, choices=Provider.choices)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField("Сума", max_digits=12, decimal_places=2)
    external_id = models.CharField("Зовнішній ID", max_length=255, blank=True)
    raw_response = models.JSONField("Відповідь API", default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"

    def __str__(self) -> str:
        return f"Платіж #{self.pk} — {self.provider} — {self.status}"
