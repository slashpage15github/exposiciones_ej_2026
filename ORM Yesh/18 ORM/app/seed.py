from flask import Blueprint, render_template, request, redirect, url_for, flash
from .extensions import db
from .models import Alumno, Curso, Inscripcion, generar_matricula

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

escuela_bp = Blueprint("escuela", __name__)

@escuela_bp.route("/")
def inicio():
    return redirect(url_for("escuela.inscripciones_list"))

@escuela_bp.route("/inscripciones/")
def inscripciones_list():
    q = request.args.get("q", "").strip()
    qs = Inscripcion.query.join(Alumno).join(Curso)
    if q:
        qs = qs.filter(Alumno.nombre.ilike(f"%{q}%"))
    inscripciones = qs.order_by(Inscripcion.id.desc()).all()
    return render_template("escuela/inscripciones_list.html", inscripciones=inscripciones, q=q)

@escuela_bp.route("/inscripciones/nueva/", methods=["GET", "POST"])
def inscripcion_create():
    cursos = Curso.query.order_by(Curso.clave).all()

    if request.method == "POST":
        nombre = (request.form.get("nombre_alumno") or "").strip()
        curso_id = request.form.get("curso_id")
        estado = request.form.get("estado") or "ACTIVA"

        if not nombre:
            flash("Escribe el nombre del alumno.", "error")
            return redirect(url_for("escuela.inscripcion_create"))
        if not curso_id:
            flash("Selecciona un curso.", "error")
            return redirect(url_for("escuela.inscripcion_create"))

        # Crear alumno si no existe
        alumno = Alumno.query.filter_by(nombre=nombre).first()
        if not alumno:
            matricula, orden, hoy = generar_matricula(db.session)
            alumno = Alumno(matricula=matricula, nombre=nombre, fecha_inscripcion=hoy, orden_dia=orden)
            db.session.add(alumno)
            db.session.commit()

        # Evitar duplicado alumno-curso
        existe = Inscripcion.query.filter_by(alumno_matricula=alumno.matricula, curso_id=int(curso_id)).first()
        if existe:
            flash("Ese alumno ya está inscrito en ese curso.", "error")
            return redirect(url_for("escuela.inscripcion_create"))

        db.session.add(Inscripcion(alumno_matricula=alumno.matricula, curso_id=int(curso_id), estado=estado))
        db.session.commit()
        flash("Inscripción creada ✅", "ok")
        return redirect(url_for("escuela.inscripciones_list"))

    return render_template("escuela/inscripcion_form.html", cursos=cursos)

@escuela_bp.route("/inscripciones/<int:inscripcion_id>/eliminar/")
def inscripcion_delete(inscripcion_id):
    ins = Inscripcion.query.get_or_404(inscripcion_id)
    db.session.delete(ins)
    db.session.commit()
    flash("Inscripción eliminada ✅", "ok")
    return redirect(url_for("escuela.inscripciones_list"))