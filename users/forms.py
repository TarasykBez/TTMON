from django import forms
from .models import CustomUser, Team
from django.utils.crypto import get_random_string


class UserCreationFormCustom(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        empty_label="Виберіть команду",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_team_select'})
    )

    assigned_creatives = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='creative'),
        required=False,
        label="Призначити креативників",
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select-creatives',
            'id': 'id_creatives_select',
            'style': 'height: 100px;'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'team', 'is_team_lead', 'assigned_creatives']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введіть логін'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}),
            'role': forms.Select(attrs={'class': 'form-select', 'id': 'id_role_select'}),
            'is_team_lead': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        password = get_random_string(length=12)
        user.set_password(password)
        user.temporary_password = password
        user.has_changed_password = False

        if commit:
            user.save()
            # Зберігаємо ManyToMany зв'язки (креативників)
            self.save_m2m()
        return user, password  # Важливо: повертаємо два значення