from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'important': 'Importante',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresá el título de la tarea'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribí una descripción...'
            }),
            'important': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
<<<<<<< HEAD
        }
=======
        }


class TaskStatusOnlyForm(forms.ModelForm):
    # Formulario limitado para el rol Ventas.
    class Meta:
        model = Task
        fields = ['datecompleted', 'description', 'title']
        
>>>>>>> 61463ff4fca98f874846df469dc5eba6d309b223
