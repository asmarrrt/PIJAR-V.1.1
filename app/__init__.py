from flask import Flask, render_template
from config import Config
from .extensions import db,migrate,login_manager,csrf
from .models import User

def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app); migrate.init_app(app,db); login_manager.init_app(app); csrf.init_app(app)
    from .auth.routes import bp as auth_bp
    from .teacher.routes import bp as teacher_bp
    from .student.routes import bp as student_bp
    from .admin.routes import bp as admin_bp
    from .exams.routes import bp as exams_bp
    from .results.routes import bp as results_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp,url_prefix="/teacher")
    app.register_blueprint(student_bp,url_prefix="/student")
    app.register_blueprint(admin_bp,url_prefix="/admin")
    app.register_blueprint(exams_bp,url_prefix="/exams")
    app.register_blueprint(results_bp,url_prefix="/results")
    @app.get("/")
    def index(): return render_template("index.html")
    @app.errorhandler(403)
    def forbidden(_): return render_template("error.html",code=403,message="Akses ditolak."),403
    @app.errorhandler(404)
    def not_found(_): return render_template("error.html",code=404,message="Halaman tidak ditemukan."),404
    @app.context_processor
    def inject_globals(): return {"roles": {"TEACHER":"TEACHER","STUDENT":"STUDENT","SUPERADMIN":"SUPERADMIN"}}
    return app

@login_manager.user_loader
def load_user(user_id): return db.session.get(User,int(user_id))
