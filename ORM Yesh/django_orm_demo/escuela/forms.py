from django import forms
from .models import Alumno, Curso, Inscripcion

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ["nombre"]
        labels = {"nombre": "Nombre del alumno"}

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["clave", "nombre", "cupo"]

class InscripcionForm(forms.Form):
    nombre_alumno = forms.CharField(
        max_length=80,
        label="Nombre del alumno",
        widget=forms.TextInput(attrs={"placeholder": "Ej. Roberto Yeshua Moreno"})
    )
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all().order_by("clave"),
        label="Curso"
    )
    estado = forms.ChoiceField(
        choices=Inscripcion.ESTADOS,
        initial="ACTIVA",
        label="Estado"
    )