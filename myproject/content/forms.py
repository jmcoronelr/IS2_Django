# forms.py
from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'category', 'status', 'plantilla']  # Asegúrate de incluir 'plantilla'
