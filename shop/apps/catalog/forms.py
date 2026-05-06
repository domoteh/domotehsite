from decimal import Decimal

from django import forms


ROUNDING_CHOICES = [
    ("none", "Без округлення"),
    ("1", "До цілих (1 грн)"),
    ("5", "До 5 грн"),
    ("10", "До 10 грн"),
    ("50", "До 50 грн"),
]


class BulkPriceForm(forms.Form):
    change_type = forms.ChoiceField(
        label="Тип зміни",
        choices=[
            ("percent", "Відсоток (%)"),
            ("fixed", "Фіксована сума (грн)"),
        ],
        widget=forms.RadioSelect,
        initial="percent",
    )
    direction = forms.ChoiceField(
        label="Напрямок",
        choices=[
            ("increase", "Підняти ▲"),
            ("decrease", "Знизити ▼"),
        ],
        widget=forms.RadioSelect,
        initial="increase",
    )
    value = forms.DecimalField(
        label="Значення",
        min_value=Decimal("0.01"),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "placeholder": "Напр. 10"}),
    )
    rounding = forms.ChoiceField(
        label="Округлення результату",
        choices=ROUNDING_CHOICES,
        initial="1",
        required=False,
    )
    apply_to_wholesale = forms.BooleanField(
        label="Також змінити гуртові ціни",
        required=False,
        initial=True,
    )
    apply_to_old_price = forms.BooleanField(
        label="Також змінити стару ціну (закреслена)",
        required=False,
        initial=False,
    )
    confirm = forms.BooleanField(
        label="Підтверджую зміну цін",
        required=True,
        error_messages={"required": "Необхідно підтвердити зміну цін."},
    )

    def clean_value(self):
        value = self.cleaned_data["value"]
        change_type = self.data.get("change_type")
        if change_type == "percent" and value >= Decimal("100") and self.data.get("direction") == "decrease":
            raise forms.ValidationError("Зниження на 100% і більше неможливе — ціна стане нульовою або від'ємною.")
        if change_type == "percent" and value > Decimal("1000"):
            raise forms.ValidationError("Відсоток не може перевищувати 1000%.")
        return value
