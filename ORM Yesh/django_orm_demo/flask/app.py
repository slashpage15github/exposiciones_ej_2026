from datetime import date
from flask import Flask, request, redirect, url_for, render_template_string, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, func

app = Flask(__name__)
app.secret_key = "dev"  # para flash messages
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///escuela_flask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------
# MODELOS (ORM)
# -----------------------
class Alumno(db.Model):
    # matrícula como PK
    matricula = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    fecha_inscripcion = db.Column(db.Date, nullable=False, default=date.today)
    orden_dia = db.Column(db.Integer, nullable=False)

    inscripciones = db.relationship("Inscripcion", back_populates="alumno", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.matricula} - {self.nombre}"


class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    cupo = db.Column(db.Integer, nullable=False, default=30)

    inscripciones = db.relationship("Inscripcion", back_populates="curso", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.clave} - {self.nombre}"


class Inscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_matricula = db.Column(db.Integer, db.ForeignKey("alumno.matricula"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"), nullable=False)
    estado = db.Column(db.String(10), nullable=False, default="ACTIVA")

    alumno = db.relationship("Alumno", back_populates="inscripciones")
    curso = db.relationship("Curso", back_populates="inscripciones")

    __table_args__ = (
        UniqueConstraint("alumno_matricula", "curso_id", name="uq_alumno_curso"),
    )


# -----------------------
# UTIL: generar matrícula YYMMDD00 + consecutivo_del_día
# -----------------------
def generar_matricula_y_orden():
    hoy = date.today()
    base = int(hoy.strftime("%y%m%d")) * 100  # YYMMDD00
    ultimo = db.session.query(func.max(Alumno.orden_dia)).filter(Alumno.fecha_inscripcion == hoy).scalar()
    orden = 1 if ultimo is None else int(ultimo) + 1
    matricula = base + orden
    return matricula, orden, hoy


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


# -----------------------
# VISTAS (Controller)
# -----------------------
BASE_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{{ title or "CRUD Escuela (Flask ORM)" }}</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f5f5f5; margin:20px; }
    .box { max-width:950px; margin:auto; background:#fff; padding:20px; border-radius:10px; }
    nav a { margin-right:12px; text-decoration:none; color:#0d6efd; font-weight:bold; }
    table { width:100%; border-collapse: collapse; margin-top:10px; }
    th, td { border:1px solid #ddd; padding:8px; }
    th { background:#f0f0f0; }
    .btn { padding:6px 10px; border:none; border-radius:6px; text-decoration:none; cursor:pointer; display:inline-block; }
    .p { background:#0d6efd; color:white; }
    .w { background:#ffc107; color:#222; }
    .d { background:#dc3545; color:white; }
    .s { background:#198754; color:white; }
    .g { background:#6c757d; color:white; }
    input, select { width:100%; padding:8px; margin:6px 0 12px; }
    .flash { background:#e7f6ec; border:1px solid #bfe7cb; padding:10px; border-radius:8px; margin:10px 0; }
    .err { background:#ffe8e8; border:1px solid #f1b5b5; }
  </style>
</head>
<body>
  <div class="box">
    <h1>CRUD Escuela (Flask + SQLAlchemy ORM)</h1>
    <nav>
      <a href="{{ url_for('inscripciones_list') }}">Inscripciones</a>
      <a href="{{ url_for('inscripcion_create') }}">Nueva inscripción</a>
    </nav>
    <hr>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for cat, msg in messages %}
          <div class="flash {% if cat == 'error' %}err{% endif %}">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
  </div>
</body>
</html>
"""

@app.route("/")
def inicio():
    return redirect(url_for("inscripciones_list"))

@app.route("/inscripciones/")
def inscripciones_list():
    q = request.args.get("q", "").strip()
    qs = Inscripcion.query.join(Alumno).join(Curso)
    if q:
        qs = qs.filter(Alumno.nombre.ilike(f"%{q}%"))
    inscripciones = qs.order_by(Inscripcion.id.desc()).all()

    html = """
    {% extends base %}
    {% block content %}
      <h2>Inscripciones</h2>
      <form method="GET" style="margin:10px 0;">
        <input name="q" placeholder="Buscar por alumno..." value="{{ q }}">
        <button type="submit">Buscar</button>
      </form>

      <a class="btn p" href="{{ url_for('inscripcion_create') }}">+ Nueva inscripción</a>

      {% if inscripciones %}
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Alumno</th>
            <th>Curso</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {% for i in inscripciones %}
          <tr>
            <td>{{ i.id }}</td>
            <td>{{ i.alumno.matricula }} - {{ i.alumno.nombre }}</td>
            <td>{{ i.curso.clave }} - {{ i.curso.nombre }}</td>
            <td>{{ i.estado }}</td>
            <td>
              <a class="btn d" href="{{ url_for('inscripcion_delete', inscripcion_id=i.id) }}">Eliminar</a>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
        <p>No hay inscripciones.</p>
      {% endif %}
    {% endblock %}
    """
    return render_template_string(html, base=BASE_HTML, q=q, inscripciones=inscripciones)

@app.route("/inscripciones/nueva/", methods=["GET", "POST"])
def inscripcion_create():
    cursos = Curso.query.order_by(Curso.clave).all()

    if request.method == "POST":
        nombre = (request.form.get("nombre_alumno") or "").strip()
        curso_id = request.form.get("curso_id")
        estado = request.form.get("estado") or "ACTIVA"

        if not nombre:
            flash("Escribe el nombre del alumno.", "error")
            return redirect(url_for("inscripcion_create"))
        if not curso_id:
            flash("Selecciona un curso.", "error")
            return redirect(url_for("inscripcion_create"))

        # crea alumno si no existe
        alumno = Alumno.query.filter_by(nombre=nombre).first()
        if not alumno:
            matricula, orden, hoy = generar_matricula_y_orden()
            alumno = Alumno(matricula=matricula, nombre=nombre, fecha_inscripcion=hoy, orden_dia=orden)
            db.session.add(alumno)
            db.session.commit()

        # crear inscripción (evita duplicado alumno-curso)
        existente = Inscripcion.query.filter_by(alumno_matricula=alumno.matricula, curso_id=int(curso_id)).first()
        if existente:
            flash("Ese alumno ya está inscrito en ese curso.", "error")
            return redirect(url_for("inscripcion_create"))

        ins = Inscripcion(alumno_matricula=alumno.matricula, curso_id=int(curso_id), estado=estado)
        db.session.add(ins)
        db.session.commit()
        flash("Inscripción creada ✅", "ok")
        return redirect(url_for("inscripciones_list"))

    html = """
    {% extends base %}
    {% block content %}
      <h2>Nueva inscripción</h2>
      <form method="POST">
        <label>Nombre del alumno:</label>
        <input name="nombre_alumno" placeholder="Ej. Roberto Yeshua Moreno">

        <label>Curso:</label>
        <select name="curso_id">
          <option value="">---------</option>
          {% for c in cursos %}
            <option value="{{ c.id }}">{{ c.clave }} - {{ c.nombre }}</option>
          {% endfor %}
        </select>

        <label>Estado:</label>
        <select name="estado">
          <option value="ACTIVA">Activa</option>
          <option value="CANCELADA">Cancelada</option>
        </select>

        <button class="btn s" type="submit">Guardar</button>
        <a class="btn g" href="{{ url_for('inscripciones_list') }}">Cancelar</a>
      </form>
    {% endblock %}
    """
    return render_template_string(html, base=BASE_HTML, cursos=cursos)

@app.route("/inscripciones/<int:inscripcion_id>/eliminar/")
def inscripcion_delete(inscripcion_id):
    ins = Inscripcion.query.get_or_404(inscripcion_id)
    db.session.delete(ins)
    db.session.commit()
    flash("Inscripción eliminada ✅", "ok")
    return redirect(url_for("inscripciones_list"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_cursos()
    app.run(debug=True)