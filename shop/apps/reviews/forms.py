from django import forms

from .models import Question, Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-select"}),
            "text": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
