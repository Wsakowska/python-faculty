"""Formularze aplikacji comments."""

from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """Formularz dodawania komentarza z oceną."""

    class Meta:
        model = Comment
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Napisz komentarz...',
            }),
            'rating': forms.Select(
                choices=[(i, f'{i} {"★" * i}') for i in range(1, 6)],
                attrs={'class': 'form-select'},
            ),
        }