from django import forms
from .models import CustomUser
from django.utils.crypto import get_random_string


class UserCreationFormCustom(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'supervisor']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = get_random_string(length=12)
        user.set_password(password)

        # Зберігаємо тимчасовий пароль в базу
        user.temporary_password = password
        user.has_changed_password = False

        if commit:
            user.save()
        return user, password
