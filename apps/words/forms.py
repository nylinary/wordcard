from django import forms

from .models import Word


class WordForm(forms.Form):
    """Форма для ввода нового слова или фразы."""

    word = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите слово или фразу на английском",
                "autocomplete": "off",
            }
        ),
    )
