import os
from flask import Flask, session, redirect, url_for, send_from_directory
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose # type: ignore
from flask_admin.contrib.sqla import ModelView # type: ignore

# Imports de tes fichiers locaux
from models import db, User, Progress, House
from routes import routes_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'une_cle_secrete_pour_la_session')

# --- Configuration de la Base de Données ---
uri = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.abspath("quibbler.db")}')

# Correction pour Render/PostgreSQL (Neon)
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation des extensions
db.init_app(app)

# --- Configuration Flask-Mail ---
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME='chrisaboukaram@gmail.com',
    MAIL_PASSWORD='omplywdzylkpivbu', # Idéalement, à mettre en variable d'env plus tard
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True
)
mail = Mail(app)

# --- Configuration Flask-Admin ---

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('routes.login'))

        user = User.query.get(user_id)
        if not user or not getattr(user, 'admin', 0):
            return redirect(url_for('routes.admin_only'))

        return self.render('admin/home.html')

# Initialisation de l'Admin
admin = Admin(app, name="Quibbler Admin", index_view=MyAdminIndexView())

class BaseAdminView(ModelView):
    """Classe de base pour gérer les accès admin sans répéter le code"""
    extra_css = ['/static/css/pages/admin.css']
    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        user_id = session.get('user_id')
        if not user_id:
            return False
        user = User.query.get(user_id)
        return user and getattr(user, 'admin', 0) == 1

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routes.admin_only'))

class UserAdmin(BaseAdminView):
    inline_models = [Progress]
    column_list = ['id', 'username', 'admin', 'authorized']

class HouseAdmin(BaseAdminView):
    column_list = ['id', 'name', 'points']

admin.add_view(UserAdmin(User, db.session))
admin.add_view(HouseAdmin(House, db.session))

app.register_blueprint(routes_bp) 
 
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

# --- Lancement de l'application ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host="0.0.0.0", port=port, debug=True)