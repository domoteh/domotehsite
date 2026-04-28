from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name", "last_name", "email", "phone",
            "delivery_method", "delivery_address",
            "nova_poshta_city", "nova_poshta_warehouse",
            "payment_method", "comment",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ім'я"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Прізвище"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "Електронна пошта"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+380..."}),
            "delivery_method": forms.Select(attrs={"class": "form-select"}),
            "delivery_address": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "nova_poshta_city": forms.TextInput(attrs={"class": "form-input", "placeholder": "Місто"}),
            "nova_poshta_warehouse": forms.TextInput(attrs={"class": "form-input", "placeholder": "Відділення"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
