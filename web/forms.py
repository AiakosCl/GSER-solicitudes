from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


#Formulario para Usuarios
class NuevoUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Ingrese su nombre.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Ingrese su Apellido.')
    username = forms.EmailField(required=True, help_text='Ingrese su correo electrónico.')

    class Meta:
        model = Usuario
        fields = ('username','first_name', 'last_name','password1','password2','rut', 'ceco_id','telefono','tipo_usuario', 'alimentacion', 'hoteleria', 'lavanderia', 'transporte', 'mantencion')
        labels = {
            'username':'Nombre de usuario (correo electrónico):',
            'first_name': 'Nombre(s):',
            'last_name':'Apellido(s):',
            'password1':'Ingrese su contraseña:',
            'password2':'Repita su contraseña:',
            'rut':'RUT:',
            'telefono':'Número de contacto:',
            'ceco_id':'Centro de Costos:',
            'tipo_usuario':'Tipo de perfil:',
            'alimentacion':'Solicita Alimentación?:',
            'hoteleria':'Solicita Hotelería?:',
            'transporte':'Solicita Transporte?:',
            'mantencion':'Solicita Mantenciòn?:',
            'lavanderia':'Usuario Lavandería?:'
        }

        error_messages = {
            'username': {
                'unique': 'El nombre de usuario ya existe',
            },
            'first_name': {
                'required': 'Este dato es obligatorio.'
            },
            'last_name': {
                'required': 'Este dato es obligatorio.'
            },
            'rut': {
                'required': 'Este dato es obligatorio.',
                'unique': 'El RUT ya existe',
                'max-lenght': 'Excede el tamaño de caracteres (%max_length%).',
            },
            'ceco_id': {
                'required': 'Este dato es obligatorio.',
            },
            'telefono': {
                'required': 'Este dato es obligatorio.',
            },
            'password1': {
                'required': 'Este dato es obligatorio.',
                'password_mismatch': 'Las contraseñas no coinciden',
                'password_too_short': 'La contraseña debe tener al menos 8 caracteres',
                'password_entirely_numeric': 'La contraseña debe tener a lo menos letra y/o un símbolo',
                'password_entirely_alphanumeric': 'La contraseña debe tener a lo menos un número y/o símbolo',
                'password_entirely_symbolic': 'La contraseña debe tener a lo menos un número y/o letra',
                'password_too_common': 'La contraseña es muy común',
            },
            'password2': {
                'required': 'Este dato es obligatorio.',
                'password_mismatch': 'Las contraseñas no coinciden',
                'password_too_short': 'La contraseña debe tener al menos 8 caracteres',
                'password_entirely_numeric': 'La contraseña debe tener a lo menos letra y/o un símbolo',
                'password_entirely_alphanumeric': 'La contraseña debe tener a lo menos un número y/o símbolo',
                'password_entirely_symbolic': 'La contraseña debe tener a lo menos un número y/o letra',
                'password_too_common': 'La contraseña es muy común',
            },
            'tipo_usuario': {
                'required': 'Este dato es obligatorio.',
            },
        }

    # Acá se replicará el nombre de usuario en el campo correo.
    def save(self, commit=True):
        user = super().save(commit=True)
        user.email = self.cleaned_data['username']
        if commit:
            user.save()
        return user


# class EditarUsuarioForm(forms.ModelForm):
#     class Meta:
#         model = Usuario
#         fields = ['first_name', 'last_name', 'email', 'telefono', 'ceco_id', 'rut', 'tipo_usuario', 'is_staff', 'is_active']

#     password = forms.CharField(required=False, widget=forms.PasswordInput, help_text='Dejar en blanco para no cambiar.')

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         if self.cleaned_data['password']:
#             user.set_password(self.cleaned_data['password'])
#         if commit:
#             user.save()
#         return user

class TicketLavanderiaForm(forms.ModelForm): #Revisar el formulario para continuar.
    pass

class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['usuario','tipo_contacto','area','emailcliente','telefono','mensaje']
        labels = {
            'usuario':'Usuario:',
            'tipo_contacto':'Motivo de tu contacto:',
            'area':'Área de Servicio:',
            'emailcliente':'Tu correo:',
            'telefono':'Tu número (para contactarte):',
            'mensaje':'Coméntanos'
        }