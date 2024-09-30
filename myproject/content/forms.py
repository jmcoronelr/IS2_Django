# forms.py
from django import forms
from .models import Content, Comentario
class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'categoria', 'status', 'plantilla']  # Asegúrate de incluir 'plantilla'
        
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu comentario aquí...'})
        }