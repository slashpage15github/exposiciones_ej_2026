from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Alumno, Curso, Inscripcion, generar_matricula

escuela_bp = Blueprint("escuela", __name__)


# -----------------------------
# Home
# -----------------------------
@escuela_bp.route("/")
def inicio():
    return redirect(url_for("escuela.inscripciones_list"))


# -----------------------------
# Seed de cursos (solo si no existen)
# -----------------------------
def seed_cursos():
    cursos = [
        ("1", "python 5"),
        ("4", "ANGULAR 12"),
        ("5", "Administración de redes y sistemas."),
        ("6", "PATRONES DE DISEÑOS"),
        ("8", "Computación en la nube."),
        ("9", "Desarrollo de software."),
        ("10", "Desarrollo móvil."),
        ("11", "Desarrollo web."),
        ("12", "DevOps."),
        ("13", "Gestión de base de datos"),
        ("14", "Diseño web"),
        ("15", "Programación web"),
        ("16", "Introducción a Photoshop, Blender o cualquier otro software"),
        ("17", "Uso de Word, Excel, etc."),
        ("18", "Programación para niños"),
        ("19", "Desarrollo móvil"),
        ("20", "Crear un sitio web sin conocimientos técnicos"),
        ("21", "Análisis de datos"),
        ("22", "Modelado e impresión 3D"),
        ("23", "Ciberseguridad"),
        ("24", "Construir una casa inteligente"),
        ("25", "Reparación de un ordenador, móvil, etc."),
        ("26", "XCZXCXZCXZC"),
        ("27", "DALAY"),
        ("28", "ALGOO"),
        ("29", "JOSE"),
        ("30", "WWWWWW"),
        ("31", "MAIRO"),
        ("32", "EEEEE"),
        ("34", "YYYY"),
        ("54", "DAVID PEREZ TINO"),
        ("59", "HUMANIDADES III"),
        ("60", "PLASTILINA I"),
        ("61", "PLASTILINA 1"),
    ]

    for clave, nombre in cursos:
        existe = Curso.query.filter_by(clave=str(clave)).first()
        if not existe:
            db.session.add(Curso(clave=str(clave), nombre=nombre, cupo=30))
    db.session.commit()


# -----------------------------
# LISTA de inscripciones
# -----------------------------
@escuela_bp.route("/inscripciones/")
def inscripciones_list():
    q = request.args.get("q", "").strip()

    query = (
        Inscripcion.query
        .join(Inscripcion.alumno)
        .join(Inscripcion.curso)
        .order_by(Inscripcion.id.desc())
    )

    if q:
        like = f"%{q}%"
        query = query.filter(Alumno.nombre.ilike(like))

    inscripciones = query.all()

    return render_template(
        "escuela/inscripciones_list.html",
        q=q,
        inscripciones=inscripciones,
    )


# -----------------------------
# CREAR inscripción
# (si el alumno no existe, se crea con matrícula automática)
# -----------------------------
@escuela_bp.route("/inscripciones/nueva/", methods=["GET", "POST"])
def inscripcion_create():
    cursos = Curso.query.order_by(Curso.id.asc()).all()
    error = None

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        curso_id = (request.form.get("curso_id") or "").strip()
        estado = (request.form.get("estado") or "ACTIVA").strip().upper()

        if not nombre:
            error = "Escribe el nombre del alumno."
        elif not curso_id:
            error = "Selecciona un curso."

        if error:
            return render_template(
                "escuela/inscripcion_form.html",
                cursos=cursos,
                error=error,
                modo="create",
                form_data={"nombre": nombre, "curso_id": curso_id, "estado": estado},
            )

        # Si ya existe un alumno con ese nombre (case-insensitive), reutilízalo.
        alumno = Alumno.query.filter(Alumno.nombre.ilike(nombre)).first()
        if alumno is None:
            matricula, orden, hoy = generar_matricula(db.session)
            alumno = Alumno(
                matricula=matricula,
                nombre=nombre,
                fecha_inscripcion=hoy,
                orden_dia=orden,
            )
            db.session.add(alumno)
            db.session.flush()  # para asegurar alumno.matricula

        ins = Inscripcion(
            alumno_matricula=alumno.matricula,
            curso_id=int(curso_id),
            estado=estado,
        )
        db.session.add(ins)

        try:
            db.session.commit()
            flash(f"Inscripción creada ✅ Matrícula: {alumno.matricula}", "ok")
            return redirect(url_for("escuela.inscripciones_list"))
        except IntegrityError:
            db.session.rollback()
            error = "Ese alumno ya está inscrito en ese curso (duplicado)."
            return render_template(
                "escuela/inscripcion_form.html",
                cursos=cursos,
                error=error,
                modo="create",
                form_data={"nombre": nombre, "curso_id": curso_id, "estado": estado},
            )

    return render_template(
        "escuela/inscripcion_form.html",
        cursos=cursos,
        error=None,
        modo="create",
        form_data={"nombre": "", "curso_id": "", "estado": "ACTIVA"},
    )


# -----------------------------
# EDITAR inscripción (sin tocar cupo)
# - NO cambia alumno (solo curso y estado)
# -----------------------------
@escuela_bp.route("/inscripciones/<int:inscripcion_id>/editar/", methods=["GET", "POST"])
def inscripcion_update(inscripcion_id: int):
    ins = Inscripcion.query.get_or_404(inscripcion_id)
    cursos = Curso.query.order_by(Curso.id.asc()).all()
    error = None

    if request.method == "POST":
        curso_id = (request.form.get("curso_id") or "").strip()
        estado = (request.form.get("estado") or "ACTIVA").strip().upper()

        if not curso_id:
            error = "Selecciona un curso."

        if error:
            return render_template(
                "escuela/inscripcion_form.html",
                cursos=cursos,
                error=error,
                modo="edit",
                inscripcion=ins,
            )

        ins.curso_id = int(curso_id)
        ins.estado = estado

        try:
            db.session.commit()
            flash("Inscripción actualizada ✅", "ok")
            return redirect(url_for("escuela.inscripciones_list"))
        except IntegrityError:
            db.session.rollback()
            error = "Ese alumno ya está inscrito en ese curso (duplicado)."
            return render_template(
                "escuela/inscripcion_form.html",
                cursos=cursos,
                error=error,
                modo="edit",
                inscripcion=ins,
            )

    return render_template(
        "escuela/inscripcion_form.html",
        cursos=cursos,
        error=None,
        modo="edit",
        inscripcion=ins,
    )


# -----------------------------
# ELIMINAR inscripción
# -----------------------------
@escuela_bp.route("/inscripciones/<int:inscripcion_id>/eliminar/", methods=["POST", "GET"])
def inscripcion_delete(inscripcion_id: int):
    ins = Inscripcion.query.get_or_404(inscripcion_id)
    db.session.delete(ins)
    db.session.commit()
    flash("Inscripción eliminada ✅", "ok")
    return redirect(url_for("escuela.inscripciones_list"))