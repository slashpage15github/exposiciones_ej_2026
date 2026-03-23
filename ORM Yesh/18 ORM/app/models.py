from datetime import date
from sqlalchemy import UniqueConstraint, func
from .extensions import db

class Alumno(db.Model):
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

def generar_matricula(db_session):
    """YYMMDD00 + consecutivo del día"""
    hoy = date.today()
    base = int(hoy.strftime("%y%m%d")) * 100
    ultimo = db_session.query(func.max(Alumno.orden_dia)).filter(Alumno.fecha_inscripcion == hoy).scalar()
    orden = 1 if ultimo is None else int(ultimo) + 1
    return base + orden, orden, hoy