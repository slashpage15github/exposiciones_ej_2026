from flask import Flask
from .extensions import db
from .routes import escuela_bp, seed_cursos
from .seed import seed_cursos

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.secret_key = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///escuela_flask.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(escuela_bp)

    with app.app_context():
        db.create_all()
        seed_cursos()

    return app