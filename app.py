from flask import *
from flask_mail import Mail, Message
from flask_admin.model.form import InlineFormAdmin # type: ignore
from flask_admin.contrib.sqla import ModelView # type: ignore
from flask_admin import Admin, AdminIndexView, expose # type: ignore
from models import db, User, Progress, House
from routes import routes_bp
import os

app = Flask(__name__)
app.secret_key = 'une_cle_secrete_pour_la_session'

# --- Base de données ---

uri = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.abspath("quibbler.db")}')

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# --- Flask-Mail ---
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'chrisaboukaram@gmail.com'
app.config["MAIL_PASSWORD"] = 'omplywdzylkpivbu'
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

# ------------------- #
# --- Class Admin --- #
# ------------------- #

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

admin = Admin(app, name="", index_view=MyAdminIndexView())

class UserAdmin(ModelView):
    inline_models = [Progress]
    extra_css = ['/static/css/pages/admin.css']
    column_list = ['id', 'username', 'admin', 'authorized']
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


class HouseAdmin(ModelView):
    extra_css = ['/static/css/pages/admin.css']
    column_list = ['id', 'name', 'points']
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

admin.add_view(UserAdmin(User, db.session))
admin.add_view(HouseAdmin(House, db.session))

# --- Blueprints ---
app.register_blueprint(routes_bp) 

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

#with app.app_context():
    #try:
        #db.create_all()
        #print("✅ Base de données et tables créées.")
        
        #if not User.query.filter_by(username="ChrisAkk").first():
            #new_user = User(username="ChrisAkk", password="Chr1s.Akk")
            #new_user.admin = 1
            #db.session.add(new_user)
            #db.session.commit()
            #print("✅ Utilisateur admin créé.")

        # for user in User.query.all():
        #     print(user.id, user.username)
        # orphan_progress = Progress.query.filter(~Progress.user.has()).all()
        # for progress in orphan_progress:
        #     db.session.delete(progress)
        # db.session.commit()
        
    #except Exception as e:
        #print(f"Erreur d'initialisation : {e}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host="0.0.0.0", port=port, debug=False)