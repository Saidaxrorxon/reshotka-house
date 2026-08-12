from django import forms

from .models import ConsultationRequest, Review


class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ["name", "phone", "message"]
        error_messages = {
            "name": {"required": "Пожалуйста, укажите имя."},
            "phone": {"required": "Пожалуйста, укажите телефон."},
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["name", "rating", "text"]
        error_messages = {
            "name": {"required": "Пожалуйста, укажите имя."},
            "text": {"required": "Пожалуйста, напишите отзыв."},
        }
