from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новий"
        CONFIRMED = "confirmed", "Підтверджений"
        PAID = "paid", "Оплачений"
        SHIPPED = "shipped", "Відправлений"
        DELIVERED = "delivered", "Доставлений"
        CANCELLED = "cancelled", "Скасований"

    class DeliveryMethod(models.TextChoices):
        NOVA_POSHTA = "nova_poshta", "Нова Пошта"
        UKRPOSHTA = "ukrposhta", "Укрпошта"
        DELIVERY = "delivery", "Доставка кур'єром"
        MEEST = "meest", "Meest"
        ROZETKA = "rozetka", "Rozetka Delivery"
        PICKUP = "pickup", "Самовивіз"

    class PaymentMethod(models.TextChoices):
        MONOBANK = "monobank", "MonoBank (онлайн)"
        COD = "cod", "Накладений платіж"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders",
    )
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    first_name = models.CharField("Ім'я", max_length=100)
    last_name = models.CharField("Прізвище", max_length=100)
    email = models.EmailField("Електронна пошта")
    phone = models.CharField("Телефон", max_length=20)
    delivery_method = models.CharField("Доставка", max_length=20, choices=DeliveryMethod.choices)
    delivery_address = models.TextField("Адреса доставки", blank=True)
    nova_poshta_city = models.CharField("Місто НП", max_length=255, blank=True)
    nova_poshta_city_ref = models.CharField("Ref міста НП", max_length=36, blank=True)
    nova_poshta_warehouse = models.CharField("Відділення НП", max_length=500, blank=True)
    nova_poshta_warehouse_ref = models.CharField("Ref відділення НП", max_length=36, blank=True)
    payment_method = models.CharField("Оплата", max_length=20, choices=PaymentMethod.choices)
    total = models.DecimalField("Сума", max_digits=12, decimal_places=2, default=0)
    tracking_number = models.CharField("ТТН", max_length=50, blank=True)
    comment = models.TextField("Коментар", blank=True)
    created_at = models.DateTimeField("Створено", auto_now_add=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Замовлення #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField("Назва товару", max_length=500)
    sku = models.CharField("Артикул", max_length=100, blank=True)
    quantity = models.PositiveIntegerField("Кількість", default=1)
    price = models.DecimalField("Ціна", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    def __str__(self) -> str:
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
