from django.db import models, transaction
from datetime import date

class Alumno(models.Model):
    # Matrícula = PK (8 dígitos)
    matricula = models.PositiveIntegerField(primary_key=True, editable=False)

    nombre = models.CharField(max_length=80)

    # guardamos la fecha real para que no dependa del “overflow” de la matrícula
    fecha_inscripcion = models.DateField(auto_now_add=True, editable=False)

    # orden del día (71, 100, etc.) para trazabilidad
    orden_dia = models.PositiveIntegerField(editable=False)

    def save(self, *args, **kwargs):
        # Si ya existe (update), no regeneres matrícula
        if self.matricula:
            return super().save(*args, **kwargs)

        fecha = self.fecha_inscripcion or date.today()
        base = int(fecha.strftime("%y%m%d")) * 100  # YYMMDD00

        with transaction.atomic():
            ultimo = Alumno.objects.filter(fecha_inscripcion=fecha).order_by("-orden_dia").first()
            self.orden_dia = 1 if not ultimo else ultimo.orden_dia + 1
            self.matricula = base + self.orden_dia

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.matricula} - {self.nombre}"


class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=20, unique=True)
    cupo = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class Inscripcion(models.Model):
    ESTADOS = [
        ("ACTIVA", "Activa"),
        ("CANCELADA", "Cancelada"),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name="inscripciones")
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="inscripciones")
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVA")

    class Meta:
        unique_together = ("alumno", "curso")  # evita doble inscripción al mismo curso

    def __str__(self):
        return f"{self.alumno} -> {self.curso} ({self.estado})"