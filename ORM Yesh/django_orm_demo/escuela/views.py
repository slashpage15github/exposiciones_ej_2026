from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.core.paginator import Paginator
from django.db import IntegrityError
from .models import Alumno, Inscripcion
from .forms import InscripcionForm

try:
    from .models import Alumno, Inscripcion
except ImportError:
    from .models import Cliente as Alumno, Orden as Inscripcion

try:
    from .forms import AlumnoForm, InscripcionForm
except ImportError:
    from .forms import ClienteForm as AlumnoForm, OrdenForm as InscripcionForm


def inicio(request):
    return redirect("alumnos_list")


# LISTADO ALUMNOS 

def alumnos_list(request):
    q = request.GET.get("q", "").strip()

    qs = Alumno.objects.all().order_by("matricula")
    if q:
        qs = qs.filter(nombre__icontains=q)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "escuela/alumno_list.html", {
        "page_obj": page_obj,
        "q": q,
    })


# CRUD ALUMNOS

def alumno_create(request):
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("alumnos_list")
    else:
        form = AlumnoForm()

    return render(request, "escuela/alumno_form.html", {"form": form, "modo": "Nuevo"})


def alumno_update(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    if request.method == "POST":
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            return redirect("alumnos_list")
    else:
        form = AlumnoForm(instance=alumno)

    return render(request, "escuela/alumno_form.html", {"form": form, "modo": "Editar"})


def alumno_delete(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    if request.method == "POST":
        alumno.delete()
        return redirect("alumnos_list")

    return render(request, "escuela/alumno_delete.html", {"alumno": alumno})


# DETALLE ALUMNO 

def alumno_detail(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    # Detecta cómo se llama el ForeignKey en Inscripcion 

    fk_field = "alumno" if hasattr(Inscripcion, "alumno") else "cliente"

    inscripciones = Inscripcion.objects.filter(**{fk_field: alumno}).order_by("id")

    # Detecta cómo se llama el monto 
    amount_field = "total" if hasattr(Inscripcion, "total") else "monto"
    total_inscripciones = inscripciones.aggregate(s=Sum(amount_field))["s"] or 0

    return render(request, "escuela/alumno_detail.html", {
        "alumno": alumno,
        "inscripciones": inscripciones,
        "total_inscripciones": total_inscripciones,
    })


# LISTADO INSCRIPCIONES

def inscripciones_list(request):
    q = request.GET.get("q", "").strip()

    fk_field = "alumno" if hasattr(Inscripcion, "alumno") else "cliente"

    qs = Inscripcion.objects.select_related(fk_field).all().order_by("id")
    if q:
        qs = qs.filter(**{f"{fk_field}__nombre__icontains": q})

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "escuela/inscripciones_list.html", {
        "page_obj": page_obj,
        "q": q,
        "fk_field": fk_field, 
    })


# CRUD INSCRIPCIONES

from django.db import IntegrityError
from .models import Alumno, Inscripcion
from .forms import InscripcionForm

def inscripcion_create(request):
    if request.method == "POST":
        form = InscripcionForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data["nombre_alumno"].strip()
            curso = form.cleaned_data["curso"]
            estado = form.cleaned_data["estado"]

            # 1) crea alumno si no existe (por nombre)
            alumno, created = Alumno.objects.get_or_create(nombre=nombre)

            # 2) crea inscripción (si ya existe, avisa)
            try:
                Inscripcion.objects.create(alumno=alumno, curso=curso, estado=estado)
                return redirect("inscripciones_list")
            except IntegrityError:
                form.add_error(None, "Este alumno ya está inscrito en ese curso.")
    else:
        form = InscripcionForm()

    return render(request, "escuela/inscripcion_form.html", {"form": form, "modo": "Nueva"})


def inscripcion_update(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    if request.method == "POST":
        form = InscripcionForm(request.POST, instance=inscripcion)
        if form.is_valid():
            form.save()
            return redirect("inscripciones_list")
    else:
        form = InscripcionForm(instance=inscripcion)

    return render(request, "escuela/inscripcion_form.html", {"form": form, "modo": "Editar"})


def inscripcion_delete(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    if request.method == "POST":
        inscripcion.delete()
        return redirect("inscripciones_list")

    return render(request, "escuela/inscripcion_delete.html", {"inscripcion": inscripcion})