"""Formularze aplikacji recipes."""

from django import forms
from .models import Recipe, RecipeIngredient, Ingredient


class RecipeForm(forms.ModelForm):
    """Formularz dodawania/edycji przepisu."""

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'instructions', 'category',
                  'prep_time', 'difficulty', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'prep_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class RecipeIngredientForm(forms.ModelForm):
    """Formularz składnika w przepisie."""

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'amount']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


# Formset — pozwala dodać wiele składników na raz
RecipeIngredientFormSet = forms.inlineformset_factory(
    Recipe, RecipeIngredient,
    form=RecipeIngredientForm,
    extra=5,
    can_delete=True,
)