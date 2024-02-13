from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django import forms
from .models import Employee, AvailabilityMessage, Event


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        raw_password = self.cleaned_data["password"]
        encrypted_password = make_password(raw_password)
        user.password = encrypted_password
        return super(UserForm, self).save(commit=True)

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }


BaseEmployeeFormSet = inlineformset_factory(User, Employee, form=EmployeeForm,
                                            fields=('name', 'email', 'company', 'country'), extra=1)


class EmployeeFormSet(BaseEmployeeFormSet):
    def add_fields(self, form, index):
        super(EmployeeFormSet, self).add_fields(form, index)

        form.fields['name'].widget.attrs['placeholder'] = 'Name'
        form.fields['email'].widget.attrs['placeholder'] = 'Email'
        form.fields['company'].widget.attrs['placeholder'] = 'Company name'
        form.fields['country'].widget.attrs['placeholder'] = 'Country'
        form.fields['DELETE'].widget = forms.HiddenInput()


class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Event name'
        self.fields['window'].widget.attrs['placeholder'] = 'Event window'
        self.fields['country'].widget.attrs['placeholder'] = 'Country'

    class Meta:
        model = Event
        fields = '__all__'
        exclude = ['start_date', 'company', 'employees']


class AvailabilityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AvailabilityForm, self).__init__(*args, **kwargs)
        self.fields['availability'] = forms.CharField(label="", help_text="", widget=forms.Textarea())

    class Meta:
        model = AvailabilityMessage
        fields = ['availability',]
