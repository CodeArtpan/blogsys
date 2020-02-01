from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    user = forms.CharField(label='用户名', max_length=12, required=True,
                           error_messages={'required': '用户名不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'user'})
                           )
    password = forms.CharField(label='密码', min_length=8, required=True,
                               error_messages={'required': '密码不能为空'},
                               widget=forms.PasswordInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'password'})
                               )
    code = forms.CharField(label='验证码', required=True,
                           error_messages={'required': '密码不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'code'})
                           )


class RegForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    user = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'username'})
                           )
    password = forms.CharField(min_length=8,
                               widget=forms.PasswordInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'password'})
                               )
    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={
                                          'class': 'form-control',
                                          'placeholder': 'repeat password'})
                                      )
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'email'
    }))
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'code'})
                           )

    def clean_password(self):
        input_password = self.cleaned_data.get('password')
        if input_password.isdigit() or input_password.isalpha():
            raise ValidationError('密码必须包含字母和数字')
        return self.cleaned_data.get('password')

    def clean_code(self):
        if self.cleaned_data.get('code') == self.request.session.get('code'):
            return self.cleaned_data.get('code')
        else:
            raise ValidationError('验证码错误')

    def clean(self):
        if self.cleaned_data.get('password') == self.cleaned_data.get('repeat_password'):
            return self.cleaned_data
        else:
            raise ValidationError('密码不一致')
