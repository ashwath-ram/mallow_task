from django import forms


class LookupEmailForm(forms.Form):
    email = forms.EmailField(
        label='Customer Email',
        widget=forms.EmailInput(attrs={'placeholder': 'customer@example.com', 'style': 'width:260px'})
    )