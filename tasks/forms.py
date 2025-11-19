from django import forms
from .models import Task, TaskInteraction

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
        }


class TaskStatusOnlyForm(forms.ModelForm):
    class Meta:
        model = Task
        # Asegúrate que 'datecompleted', 'description', y 'title' estén aquí
        fields = ['datecompleted', 'description', 'title'] 
        
        # AÑADIR ESTE BLOQUE: widgets
        widgets = {
            # Aplicamos la clase de Bootstrap al widget del Título
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg'
            }),
            # Aplicamos la clase de Bootstrap al widget de la Descripción
            'description': forms.Textarea(attrs={
                'class': 'form-control'
            }),
            # Para el campo de fecha, si quieres un control de fecha, usa DateInput
            'datecompleted': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
        

class TaskInteractionForm(forms.ModelForm):
    class Meta:
        model = TaskInteraction
        fields = ['message'] # Solo necesitamos el campo de texto
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Escribe tu respuesta aquí...'})
        }