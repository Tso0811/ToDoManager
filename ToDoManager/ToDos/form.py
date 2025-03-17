from django import forms
from ToDos.models import ToDo

class TodoForm(forms.ModelForm):
    class Meta:
        model = ToDo
        fields = ['title', 'description', 'due_date', 'priority', 'completed']

        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }