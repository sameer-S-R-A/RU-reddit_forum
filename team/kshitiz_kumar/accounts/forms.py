from django import forms
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, min_length=6, help_text="Use at least 6 characters.")
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput, min_length=6)
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
