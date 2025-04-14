from django import forms
from .models import Term


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['term', 'definition', 'theme']
        widgets = {
            'definition': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_term(self):
        term = self.cleaned_data['term']
        if Term.objects.filter(term__iexact=term).exists():
            raise forms.ValidationError("Этот термин уже существует в базе")
        return term

class TestSettingsForm(forms.Form):
    NUM_QUESTIONS_CHOICES = [(i, str(i)) for i in range(5, 21, 1)]
    num_questions = forms.ChoiceField(
        label="Количество вопросов",
        choices=NUM_QUESTIONS_CHOICES,
        initial=10
    )