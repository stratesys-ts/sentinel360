from django import forms
from .models import Activity, TimeEntry, Timesheet

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['start_date']
        widgets = {
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        today = timezone.now().date()
        start_of_week = today - timezone.timedelta(days=today.isoweekday() - 1)
        # Ensure date is rendered in ISO for the date input
        self.fields['start_date'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['start_date'].widget.format = '%Y-%m-%d'
        self.fields['start_date'].initial = start_of_week
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            from django.utils import timezone
            today = timezone.now().date()
            # Check if start_date is in a previous month
            if (start_date.year < today.year) or \
               (start_date.year == today.year and start_date.month < today.month):
                raise forms.ValidationError("Não é permitido criar folhas de ponto para meses anteriores ao atual.")
        return start_date

class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['project', 'task', 'activity', 'date', 'hours', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
