from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),

    # alumnos
    path("alumnos/", views.alumnos_list, name="alumnos_list"),
    path("alumnos/nuevo/", views.alumno_create, name="alumno_create"),
    path("alumnos/<int:pk>/editar/", views.alumno_update, name="alumno_update"),
    path("alumnos/<int:pk>/eliminar/", views.alumno_delete, name="alumno_delete"),
    path("alumnos/<int:pk>/", views.alumno_detail, name="alumno_detail"),

    # inscripciones (plural en URL)
    path("inscripciones/", views.inscripciones_list, name="inscripciones_list"),
    path("inscripciones/nueva/", views.inscripcion_create, name="inscripcion_create"),
    path("inscripciones/<int:pk>/editar/", views.inscripcion_update, name="inscripcion_update"),
    path("inscripciones/<int:pk>/eliminar/", views.inscripcion_delete, name="inscripcion_delete"),
]