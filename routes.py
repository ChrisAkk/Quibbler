from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from models import db, User, Progress, House
from jeux import get_quiz_by_name, patronus_description, maisons_description, alignement_description, matiere_description
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Message
from films import get_signed_url
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from random import choice
from cloudinary.utils import cloudinary_url # type: ignore
import cloudinary # type: ignore
import cloudinary.uploader # type: ignore
import json
import os



routes_bp = Blueprint('routes', __name__)

cloudinary.config( 
  cloud_name = "dokfo4ty2", 
  api_key = "355469787885527", 
  api_secret = "Wggzgre2F7XL6VVWvmEZk4GaDKk",
  secure = True
)

# -------------------------------- #
# --- Inscription et Connexion --- #
# -------------------------------- #pip
# Route de connexion
@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_erreur = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('routes.to_home'))
        else:
            login_erreur = "Nom d'utilisateur ou mot de passe incorrect"

    return render_template('index/login.html', login_erreur=login_erreur)

# Route d'inscription
@routes_bp.route('/sign', methods=['GET', 'POST'])
def sign_up():
    sign_up_erreur = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_exist = User.query.filter_by(username=username).first()
        if user_exist:
            sign_up_erreur = "Ce nom est déjà utilisé !"
        else:
            if len(username) < 8:
                sign_up_erreur = "Le nom d'utilisateur doit contenir au moins 8 caractères."
                return render_template('index/signup.html', sign_up_erreur=sign_up_erreur)
        
            if not any(c in ascii_lowercase for c in password):
                sign_up_erreur = "Le mot de passe doit contenir au moins une minuscule."
                return render_template('index/signup.html', sign_up_erreur=sign_up_erreur)
            
            if not any(c in ascii_uppercase for c in password):
                sign_up_erreur = "Le mot de passe doit contenir au moins une majuscule."
                return render_template('index/signup.html', sign_up_erreur=sign_up_erreur)
            
            if not any(c in digits for c in password):
                sign_up_erreur = "Le mot de passe doit contenir au moins un chiffre."
                return render_template('index/signup.html', sign_up_erreur=sign_up_erreur)
            
            if not any(c in punctuation for c in password):
                sign_up_erreur = "Le mot de passe doit contenir au moins un caractère spécial."
                return render_template('index/signup.html', sign_up_erreur=sign_up_erreur)
              
            new_user = User(username=username)
            new_user.password = password  
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            return redirect(url_for('routes.to_home'))

    return render_template('index/signup.html', sign_up_erreur=sign_up_erreur)

# ---------------------------------------------------------------------------------------- #
# ---  Route profil avec changement photo de profil, mot de passe et nom d'utilisateur --- #
# ---------------------------------------------------------------------------------------- #

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@routes_bp.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user = User.query.get(session['user_id'])

    if "file" not in request.files:
        return redirect(url_for('routes.profil'))
    
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        upload_result = cloudinary.uploader.upload(file)
        
        user.profil_picture = upload_result['secure_url']
        db.session.commit()
    
    return redirect(url_for('routes.to_profil'))
       
@routes_bp.route('/profil', methods=['GET', 'POST'])
def to_profil():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('routes.login'))
    
    progress_maison = Progress.query.filter_by(user_id=user.id, quiz_name="maison").first()
    if not progress_maison:
        progress_maison = Progress(user_id=user.id, quiz_name="maison", maison=None)
        db.session.add(progress_maison)
        db.session.commit()

    progress_patronus = Progress.query.filter_by(user_id=user.id, quiz_name="patronus").first()
    if not progress_patronus:
        progress_patronus = Progress(user_id=user.id, quiz_name="patronus", patronus=None)
        db.session.add(progress_patronus)
        db.session.commit()

    progress_alignement = Progress.query.filter_by(user_id=user.id, quiz_name="alignement").first()
    if not progress_alignement:
        progress_alignement = Progress(user_id=user.id, quiz_name="alignement", alignement=None)
        db.session.add(progress_alignement)
        db.session.commit()

    maison = progress_maison.maison if progress_maison.maison else "poudlard"
    patronus = progress_patronus.patronus if progress_patronus.patronus else "patronus"
    alignement = progress_alignement.alignement if progress_alignement.alignement else "alignement"

    cards = [
        {'indice': 0, 'noms': ''},
        {'indice': 1, 'noms': 'Merlin'},
        {'indice': 2, 'noms': 'Cornelius Agrippa'},
        {'indice': 3, 'noms': 'Elfrida Clagg'},
        {'indice': 4, 'noms': 'Grogan Stump'},
        {'indice': 5, 'noms': 'Gulliver Pokeby'},
        {'indice': 6, 'noms': 'Glanmore Peakes'},
        {'indice': 7, 'noms': 'Hesper Starkey'},
        {'indice': 8, 'noms': 'Derwent Shimpling'},
        {'indice': 9, 'noms': 'Gunhilda de Gorsemoor'},
        {'indice': 10, 'noms': 'Burdock Muldoon'},
        {'indice': 11, 'noms': "Herpo l'Infame"},
        {'indice': 12, 'noms': 'Merwyn le Malicieux'},
        {'indice': 13, 'noms': "Andros l'Invincible"},
        {'indice': 14, 'noms': 'Fulbert Latrouille'},
        {'indice': 15, 'noms': 'Paracelse'},
        {'indice': 16, 'noms': 'Cliodna'},
        {'indice': 17, 'noms': 'Morgane'},
        {'indice': 18, 'noms': 'Ulric le Follingue'},
        {'indice': 19, 'noms': 'Norbert Dragonneau'},
        {'indice': 20, 'noms': 'Gwendoline la Fantasque'},
        {'indice': 21, 'noms': 'Stoddard Withers'},
        {'indice': 22, 'noms': 'Circé'},
        {'indice': 23, 'noms': 'Glenda Chittock'},
        {'indice': 24, 'noms': 'Adalbert Lasornette'},
        {'indice': 25, 'noms': 'Perpetua Fancourt'},
        {'indice': 26, 'noms': 'Almerick Sawbridge'},
        {'indice': 27, 'noms': 'Mirabella Plunkett'},
        {'indice': 28, 'noms': 'Tilly Toke'},
        {'indice': 29, 'noms': 'Archibald Alderton'},
        {'indice': 30, 'noms': 'Artemisia Lufkin'},
        {'indice': 31, 'noms': 'Balfour Blane'},
        {'indice': 32, 'noms': 'Brigitte Wenlock'},
        {'indice': 33, 'noms': 'Beaumont Marjoribanks'},
        {'indice': 34, 'noms': 'Donaghan Tremlett'},
        {'indice': 35, 'noms': 'Bowman Wright'},
        {'indice': 36, 'noms': 'Jocelyn Wadcock'},
        {'indice': 37, 'noms': 'Cassandra Vablatsky'},
        {'indice': 38, 'noms': 'Chauncey Oldridge'},
        {'indice': 39, 'noms': 'Gwenog Jones'},
        {'indice': 40, 'noms': 'Carlotta Pinkstone'},
        {'indice': 41, 'noms': 'Godric Gryffondor'},
        {'indice': 42, 'noms': 'Crispin Cronk'},
        {'indice': 43, 'noms': 'Cyprien Youdle'},
        {'indice': 44, 'noms': 'Devlin Corneblanche'},
        {'indice': 45, 'noms': 'Dunbar Oglethorpe'},
        {'indice': 46, 'noms': 'Miranda Fauconnette'},
        {'indice': 47, 'noms': 'Edgar Stroulger'},
        {'indice': 48, 'noms': 'Salazar Serpentard'},
        {'indice': 49, 'noms': 'Elladora Ketteridge'},
        {'indice': 50, 'noms': 'Musidora Barkwith'},
        {'indice': 51, 'noms': 'Ethelred Toujourprêt'},
        {'indice': 52, 'noms': 'Félix Labeille'},
        {'indice': 53, 'noms': 'Greta Grandamour'},
        {'indice': 54, 'noms': 'Gaspard Shingleton'},
        {'indice': 55, 'noms': 'Honoria Nutcombe'},
        {'indice': 56, 'noms': 'Gédéon Miette'},
        {'indice': 57, 'noms': 'Gifford Ollerton'},
        {'indice': 58, 'noms': 'Glover Hipworth'},
        {'indice': 59, 'noms': 'Gregory le Hautain'},
        {'indice': 60, 'noms': 'Laverne de Montmorency'},
        {'indice': 61, 'noms': 'Havelock Sweeting'},
        {'indice': 62, 'noms': 'Ignatia Wildsmith'},
        {'indice': 63, 'noms': 'Herman Wintringham'},
        {'indice': 64, 'noms': 'Jocunda Sykes'},
        {'indice': 65, 'noms': 'Gondoline Oliphant'},
        {'indice': 66, 'noms': 'Flavius Belby'},
        {'indice': 67, 'noms': 'Justus Pilliwickle'},
        {'indice': 68, 'noms': 'Kirley Duke'},
        {'indice': 69, 'noms': 'Bertie Crochue'},
        {'indice': 70, 'noms': 'Léopoldine Smethwyck'},
        {'indice': 71, 'noms': 'Reine Maëva'},
        {'indice': 72, 'noms': 'Helga Poufsouffle'},
        {'indice': 73, 'noms': 'Mopsus'},
        {'indice': 74, 'noms': 'Montague Knightley'},
        {'indice': 75, 'noms': 'Mungo Bonham'},
        {'indice': 76, 'noms': 'Myron Wagtail'},
        {'indice': 77, 'noms': 'Norvel Twonk'},
        {'indice': 78, 'noms': 'Orsino Thruston'},
        {'indice': 79, 'noms': 'Oswald Beamish'},
        {'indice': 80, 'noms': 'Béatrice Bloxam'},
        {'indice': 81, 'noms': 'Quong Po'},
        {'indice': 82, 'noms': 'Rowena Serdaigle'},
        {'indice': 83, 'noms': 'Rodrigue Plumpton'},
        {'indice': 84, 'noms': 'Roland Tonneau'},
        {'indice': 85, 'noms': 'Blenheim Stalk'},
        {'indice': 86, 'noms': 'Dorcas Bienaimée'},
        {'indice': 87, 'noms': 'Thadée Thurkell'},
        {'indice': 88, 'noms': 'Célestina Moldubec'},
        {'indice': 89, 'noms': 'Alberta Toothill'},
        {'indice': 90, 'noms': 'Sacharissa Tugwood'},
        {'indice': 91, 'noms': 'Wilfred Elphick'},
        {'indice': 92, 'noms': 'Xavier Rastrick'},
        {'indice': 93, 'noms': 'Heathcote Barbary'},
        {'indice': 94, 'noms': 'Merton Graves'},
        {'indice': 95, 'noms': 'Yardley Platt'},
        {'indice': 96, 'noms': 'Hengist de Woodcroft'},
        {'indice': 97, 'noms': 'Alberic Grunnion'},
        {'indice': 98, 'noms': 'Dymphna Furmage'},
        {'indice': 99, 'noms': 'Daisy Dodderidge'},
        {'indice': 100, 'noms': 'Harry Potter'},
        {'indice': 101, 'noms': 'Albus Dumbledore'}
    ]

    carte = cards[user.carte]['noms']
    

    archive_nom_film_favori = user.film
    film = ""
    if archive_nom_film_favori == "harry_potter_un.mp4":
        film = "Harry Potter à l'école des sorciers"
    elif archive_nom_film_favori == "harry_potter_deux.mp4":
        film = "Harry Potter et la chambre des secrets"
    elif archive_nom_film_favori == "harry_potter_trois.mp4":
        film = "Harry Potter et le prisonnier d'Azkaban"
    elif archive_nom_film_favori == "harry_potter_quatre.mp4":
        film = "Harry Potter et la coupe de feu"
    elif archive_nom_film_favori == "harry_potter_cinq.mp4":
        film = "Harry Potter et l'ordre du Phénix"
    elif archive_nom_film_favori == "harry_potter_six.mp4":
        film = "Harry Potter et le prince de sang-mêlé"
    elif archive_nom_film_favori == "harry_potter_sept.mp4":
        film = "Harry Potter et les Reliques de la Mort — Partie 1"
    elif archive_nom_film_favori == "harry_potter_huit.mp4":
        film = "Harry Potter et les Reliques de la Mort — Partie 2"
    elif archive_nom_film_favori == "harry_potter_neuf.mp4":
        film = "Harry Potter — 20ème anniversaire : Retour à Poudlard"
    elif archive_nom_film_favori == "les_animaux_fantastiques_un.mp4":
        film = "Les Animaux Fantastiques"
    elif archive_nom_film_favori == "les_animaux_fantastiques_deux.mp4":
        film = "Les Animaux Fantastiques : Les Crimes de Grindelwald"
    elif archive_nom_film_favori == "les_animaux_fantastiques_trois.mp4":
        film = "Les Animaux Fantastiques : Les Secrets de Dumbledore"


    archive_nom_livre_favori = user.livre
    livre = ""
    if archive_nom_livre_favori == "1.pdf":
        livre = "Harry Potter à l'école des sorciers"
    elif archive_nom_livre_favori == "2.pdf":
        livre = "Harry Potter et la Chambre des secrets"
    elif archive_nom_livre_favori == "3.pdf":
        livre = "Harry Potter et le Prisonnier d'Azkaban"
    elif archive_nom_livre_favori == "4.pdf":
        livre = "Harry Potter et la Coupe de feu"
    elif archive_nom_livre_favori == "5.pdf":
        livre = "Harry Potter et l'Ordre du Phénix"
    elif archive_nom_livre_favori == "6.pdf":
        livre = "Harry Potter et le Prince de sang-mêlé"
    elif archive_nom_livre_favori == "7.pdf":
        livre = "Harry Potter et les Reliques de la Mort"
    elif archive_nom_livre_favori == "8.pdf":
        livre = "Harry Potter et l'Enfant maudit"
    elif archive_nom_livre_favori == "9.pdf":
        livre = "Les Animaux fantastiques — Texte du film"
    elif archive_nom_livre_favori == "10.pdf":
        livre = "Les Animaux fantastiques : Les Crimes de Grindelwald — Texte du film"
    elif archive_nom_livre_favori == "11.pdf":
        livre = "Les Animaux fantastiques : Les Secrets de Dumbledore — Texte du film"
    elif archive_nom_livre_favori == "12.pdf":
        livre = "Les Animaux fantastiques : Vie et habitat"
    elif archive_nom_livre_favori == "13.pdf":
        livre = "Le Quidditch à travers les âges"
    elif archive_nom_livre_favori == "14.pdf":
        livre = "Les Contes de Beedle le Barde"

    username_message = None
    username_change = 0

    password_message = None
    password_change = 0

    if request.method == "POST":

        if "profil_picture" in request.files:
            file = request.files["profil_picture"]
            if file.filename != "":
                filepath = os.path.join('static/uploads', secure_filename(file.filename))
                file.save(filepath)

                user.profil_picture = file.filename
                db.session.commit()
                flash("Photo de profile mise à jour avec succès.", "profile_picture_success")

        form_type = request.form.get("form_type")

        if form_type == "password_change":
            old_username = request.form.get("old_username")
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")

            if old_username != user.username:
                password_message = "Ancien nom d'utilisateur incorrect."
                password_change = 1
            elif not user.check_password(old_password):
                password_message = "Ancien mot de passe incorrect."
                password_change = 1
            else:
                valid = True
                if valid and not any(c in ascii_lowercase for c in new_password):
                    password_change = 1
                    password_message = "Le mot de passe doit contenir au moins une majuscule."
                    valid = False
                
                if valid and not any(c in ascii_uppercase for c in new_password):
                    password_change = 1
                    password_message = "Le mot de passe doit contenir au moins une minuscule."
                    valid = False
                
                if valid and not any(c in digits for c in new_password):
                    password_change = 1
                    password_message = "Le mot de passe doit contenir au moins un chiffre."
                    valid = False
                
                if valid and not any(c in punctuation for c in new_password):
                    password_change = 1
                    password_message = "Le mot de passe doit contenir au moins un caractère spécial."
                    valid = False
                
                if valid :
                    user.password = new_password
                    db.session.commit()
                    password_change = 2
                    password_message = "Mot de passe modifié avec succès."

        elif form_type == "username_change":
            old_username = request.form.get("old_username")
            new_username = request.form.get("new_username")
            password = request.form.get("password_username")

            if old_username != user.username:
                username_message = "Ancien nom d'utilisateur incorrect."
                username_change = 1
            elif not user.check_password(password):
                username_message = "Mot de passe incorrect."
                username_change = 1
            elif User.query.filter_by(username=new_username).first():
                username_message = "Ce nouveau nom d'utilisateur est déjà pris."
                username_change = 1
            else:
                if len(new_username) < 8:
                    username_change = 1
                    username_message = "Le nom d'utilisateur doit contenir au moins 8 caractères."
                else:
                    user.username = new_username
                    db.session.commit()
                    session['username'] = new_username
                    username_change = 2
                    username_message = "Nom d'utilisateur modifié avec succès."

    return render_template('pages/profil.html', username=user.username, user=user, maison=maison, patronus=patronus, alignement=alignement, film=film, livre=livre, carte=carte, username_message=username_message, password_message=password_message, username_change=username_change, password_change=password_change )

@routes_bp.route('/set_animal_favorite', methods=['POST'])
def set_animal_favorite():
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403

    user = User.query.get(session['user_id'])
    data = request.get_json()
    animal = data.get("animal")
    user.animal = animal 
    db.session.commit()
    return jsonify({"status": "ok"})

@routes_bp.route('/get_animal_favorite')
def get_animal_favorite():
    if 'user_id' not in session:
        return jsonify({"animal": None})
    user = User.query.get(session['user_id'])
    return jsonify({"animal": user.animal})

@routes_bp.route('/toggle_spark', methods=['POST'])
def toggle_spark():
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403

    user = User.query.get(session['user_id'])
    data = request.get_json()
    user.spark = data.get('enabled', True)
    db.session.commit()
    return jsonify({"status": "ok", "enabled": user.spark})

@routes_bp.route('/get_spark')
def get_spark():
    if 'user_id' not in session:
        return jsonify({"enabled": True}) 
    user = User.query.get(session['user_id'])
    return jsonify({"enabled": user.spark})

@routes_bp.route('/delete_account')
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('routes.login'))
    
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id', None)
    return logout()

# ----------------- #
# --- Jeux Quiz --- #
# ----------------- #

@routes_bp.route('/jeux', methods = ['GET', 'POST'])
def to_jeux():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user = User.query.get(session['user_id'])

    # --- points --- 

    gryff = House.query.filter_by(name="Gryffondor").first() 
    if not gryff: 
        gryff = House(name="Gryffondor", points=0)
        db.session.add(gryff)
        db.session.commit()

    pouf = House.query.filter_by(name="Poufsouffle").first() 
    if not pouf: 
        pouf = House(name="Poufsouffle", points=0)
        db.session.add(pouf)
        db.session.commit()

    serd = House.query.filter_by(name="Serdaigle").first() 
    if not serd: 
        serd = House(name="Serdaigle", points=0)
        db.session.add(serd)
        db.session.commit()

    serp = House.query.filter_by(name="Serpentard").first() 
    if not serp: 
        serp = House(name="Serpentard", points=0)
        db.session.add(serp)
        db.session.commit()

    points_perso_progress = Progress.query.filter_by(user_id=user.id, quiz_name="points_perso").first()
    if not points_perso_progress:
        points_perso_progress = Progress(user_id=user.id, quiz_name="points_perso", points_perso=0)
        db.session.add(points_perso_progress)
        db.session.commit()
    else:
        db.session.refresh(points_perso_progress)

    points = points_perso_progress.points_perso

    progress_maison = Progress.query.filter_by(user_id=user.id, quiz_name="maison").first()

    if progress_maison:
        maison = progress_maison.maison 
    else:
        maison = ""
    points_gryff, points_pouf, points_serd, points_serp = gryff.points, pouf.points, serd.points, serp.points

    # --- quiz ---

    new_progress_list = []

    quiz_express = [
        {"name": "sortilege-express", "title": "Maîtrise des Sorts I", "image": "sortilege-2.jpg"},

        {"name": "lieu-express", "title": "Atlas des Lieux I", "image": "lieu-2.jpg"},

        {"name": "creature-express", "title": "Magizoologie Avancée I", "image": "creature-2.jpg"}, 
        {"name": "creature-express-2", "title": "Magizoologie Avancée II", "image": "creature-2.jpg"},

        {"name": "potion-express", "title": "Potions et Alchimie I", "image": "potion-2.jpg"},
        {"name": "potion-express-2", "title": "Potions et Alchimie II", "image": "potion-2.jpg"},

        {"name": "gastronomie-express", "title": "Saveurs Magique I", "image": "gastronomie-2.jpg"},

        {"name": "histoire-express", "title": "Mémoires de Sorciers I", "image": "histoire-2.jpg"},

        {"name": "personnage-express", "title": "Noblesse et Lignées I", "image": "personnage-2.jpg"},
        {"name": "personnage-express-2", "title": "Noblesse et Lignées II", "image": "personnage-2.jpg"},

        {"name": "droit-express", "title": "Droit et Ministère I", "image": "personnage-2.jpg"},

        {"name": "objet-express", "title": "Artefacts et Reliques I", "image": "personnage-2.jpg"}
    ]

    quiz_choixpeau = [
        {"name": "maison", "title": "test des maisons", "image": "choixpeau.png"}
    ]

    quiz_patronus = [
        {"name": "patronus", "title": "test de patronus", "image": "patronus.png"}
    ]

    quiz_alignement = [
        {"name": "alignement", "title": "test d'alignement", "image": "alignement.png"}
    ]

    quiz_matiere = [
        {"name": "matiere", "title": "test matiere préféré", "image": "matiere.png"}
    ]

    #quiz express 

    for quiz in quiz_express:
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=quiz["name"]).first()
        if progress:
            quiz["best_score"] = progress.best_score 

        else:
            new_progress_list.append(Progress(user_id=user.id, quiz_name=quiz["name"], best_score=0))
            quiz['best_score'] = 0

        quiz_data = get_quiz_by_name(quiz["name"])
        if quiz_data:
            quiz["total_questions"] = len(quiz_data['questions']) 
        else:
            quiz["total_questions"] = 0

    #quiz choixpeau

    for quiz in quiz_choixpeau:
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=quiz["name"]).first()
        if progress:
            quiz["maison"] = progress.maison or ""

        else:
            new_progress_list.append(Progress(user_id=user.id, quiz_name=quiz["name"], maison=""))
            quiz['maison'] = ""

        quiz_data = get_quiz_by_name(quiz["name"])
        if quiz_data:
            quiz["total_questions"] = len(quiz_data['questions']) 
        else:
            quiz["total_questions"] = 0


    #quiz Patronus

    for quiz in quiz_patronus:
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=quiz["name"]).first()
        if progress:
            quiz["patronus"] = progress.patronus or ""

        else:
            new_progress_list.append(Progress(user_id=user.id, quiz_name=quiz["name"], patronus=""))
            quiz['patronus'] = ""

        quiz_data = get_quiz_by_name(quiz["name"])
        if quiz_data:
            quiz["total_questions"] = len(quiz_data['questions']) 
        else:
            quiz["total_questions"] = 0

    #quiz Alignement

    for quiz in quiz_alignement:
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=quiz["name"]).first()
        if progress:
            quiz["alignement"] = progress.alignement or ""

        else:
            new_progress_list.append(Progress(user_id=user.id, quiz_name=quiz["name"], alignement=""))
            quiz['alignement'] = ""

        quiz_data = get_quiz_by_name(quiz["name"])
        if quiz_data:
            quiz["total_questions"] = len(quiz_data['questions']) 
        else:
            quiz["total_questions"] = 0

    #quiz Matiere

    for quiz in quiz_matiere:
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=quiz["name"]).first()
        if progress:
            quiz["matiere"] = progress.matiere or ""

        else:
            new_progress_list.append(Progress(user_id=user.id, quiz_name=quiz["name"], matiere=""))
            quiz['matiere'] = ""

        quiz_data = get_quiz_by_name(quiz["name"])
        if quiz_data:
            quiz["total_questions"] = len(quiz_data['questions']) 
        else:
            quiz["total_questions"] = 0

    if new_progress_list:
        db.session.add_all(new_progress_list)
        db.session.commit()

    return render_template("pages/jeux/jeux.html", 
                           username=user.username, 
                           user=user, 
                           quiz_choixpeau=quiz_choixpeau, 
                           quiz_express=quiz_express, 
                           quiz_patronus=quiz_patronus, 
                           quiz_alignement=quiz_alignement,
                           quiz_matiere=quiz_matiere,
                           maison=maison, 
                           points=points,
                           points_gryff=points_gryff,
                           points_pouf=points_pouf,
                           points_serd=points_serd,
                           points_serp=points_serp)

@routes_bp.route('/buy', methods = ['GET', 'POST'])
def buy():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])

    points_perso_progress = Progress.query.filter_by(user_id=user.id, quiz_name="points_perso").first()
    if not points_perso_progress:
        points_perso_progress = Progress(user_id=user.id, quiz_name="points_perso", points_perso=0)
        db.session.add(points_perso_progress)
        db.session.commit()
    else:
        db.session.refresh(points_perso_progress)

    mode = request.args.get('mode', type=int)
    erreur = ''

    if mode == 1:
        if points_perso_progress.points_perso >= 25:
            points_perso_progress.points_perso -= 25
            carte = pack()
            niveau = rarete(carte)
            if carte not in user.cards:
                user.cards.append(carte)
                message = "Bravo"
            else:
                message = "Dommage"
                user.cards.append(carte)
            db.session.commit()
            return render_template("pages/jeux/buy.html", username=user.username, user=user, mode=mode, erreur=erreur, carte=carte, message=message, niveau=niveau)
        else:
            erreur = 'Pas assès de points !'

    else:
        return 'On est désolé, on a un probleme', 404
    
    return render_template("pages/jeux/buy.html", username=user.username, user=user, erreur=erreur, mode=mode)

def pack():
    cartes_or = [11, 15, 40, 41, 48, 69, 72, 74, 82, 100, 101]
    cartes_argents = [3, 8, 13, 14, 16, 17, 20, 22, 23, 27, 30, 34, 35, 36, 38, 39, 42, 43, 45, 52, 54, 55, 56, 59, 60, 62, 65, 68, 70, 71, 73, 79, 85, 87, 89, 90, 92, 97, 98, 99]
    cartes_bronze = [1, 2, 4, 5, 6, 7, 9, 10, 12, 18, 19, 21, 24, 25, 26, 28, 29, 31, 32, 33, 37, 44, 46, 47, 49, 50, 51, 53, 57, 58, 61, 63, 64, 66, 67, 75, 76, 77, 78, 80, 81, 83, 84, 86, 88, 91, 93, 94, 95, 96]

    cartes = cartes_or + cartes_argents + cartes_bronze*2
    carte = choice(cartes)

    return carte

def rarete(carte):
    cartes_or = [11, 15, 40, 41, 48, 69, 72, 74, 82, 100, 101]
    cartes_argents = [3, 8, 13, 14, 16, 17, 20, 22, 23, 27, 30, 34, 35, 36, 38, 39, 42, 43, 45, 52, 54, 55, 56, 59, 60, 62, 65, 68, 70, 71, 73, 79, 85, 87, 89, 90, 92, 97, 98, 99]
    cartes_bronze = [1, 2, 4, 5, 6, 7, 9, 10, 12, 18, 19, 21, 24, 25, 26, 28, 29, 31, 32, 33, 37, 44, 46, 47, 49, 50, 51, 53, 57, 58, 61, 63, 64, 66, 67, 75, 76, 77, 78, 80, 81, 83, 84, 86, 88, 91, 93, 94, 95, 96]

    if carte in cartes_or:
        niveau = 3
    elif carte in cartes_argents:
        niveau = 2
    elif carte in cartes_bronze:
        niveau = 1
    return niveau

@routes_bp.route('/album')
def to_album():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])

    carte_favorite = user.carte

    cards = [
        {'indice': None, 'noms': 'none', 'description': 'none'},
        {'indice': 1, 'doublons': user.cards.count(1), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Merlin', 'description': 'Moyen Âge, dates inconnues. Le plus célèbre sorcier de tous les temps. Également connu sous le nom de Prince des Enchanteurs. Œuvrait à la cour du Roi Arthur.'},
        {'indice': 2, 'doublons': user.cards.count(2), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Cornelius Agrippa', 'description': '1486 - 1535. Sorcier célèbre qui fut emprisonné par les non magiciens pour ses écrits.'},
        {'indice': 3, 'doublons': user.cards.count(3), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Elfrida Clagg', 'description': '1612 - 1687. Chef du Conseil des sorciers.'},
        {'indice': 4, 'doublons': user.cards.count(4), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Grogan Stump', 'description': '1770 - 1884. Ministre de la Magie très populaire, nommé en 1811.'},
        {'indice': 5, 'doublons': user.cards.count(5), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gulliver Pokeby', 'description': "1750 - 1839. Expert des oiseaux magiques. Déchiffra en premier le chant de l'Augurey."},
        {'indice': 6, 'doublons': user.cards.count(6), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Glanmore Peakes', 'description': '1677 - 1761. Célèbre pour avoir tué le serpent de mer de Cromer.'},
        {'indice': 7, 'doublons': user.cards.count(7), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Hesper Starkey', 'description': "1881 - 1973. Étudia l'influence des phases de la lune sur la fabrication des potions."},
        {'indice': 8, 'doublons': user.cards.count(8), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Derwent Shimpling', 'description': "1912 - aujourd'hui. Mangea une Tentacula vénéneuse, survécut mais resta violet."},
        {'indice': 9, 'doublons': user.cards.count(9), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gunhilda de Gorsemoor', 'description': '1556 - 1639. Sorcière bossue et borgne qui trouva un remède à la varicelle du dragon.'},
        {'indice': 10, 'doublons': user.cards.count(10), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Burdock Muldoon', 'description': '1429 - 1490. Chef du Conseil des sorciers de 1448 à 1450.'},
        {'indice': 11, 'doublons': user.cards.count(11), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': "Herpo l'Infame", 'description': 'Grèce antique. Premier créateur connu du Basilic.'},
        {'indice': 12, 'doublons': user.cards.count(12), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Merwyn le Malicieux', 'description': "Moyen Âge, dates inconnues. On lui attribue l'invention de nombreux maléfices et sortilèges."},
        {'indice': 13, 'doublons': user.cards.count(13), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': "Andros l'Invincible", 'description': 'Grèce antique. Serait le seul sorcier au monde à avoir élevé un Patronus géant.'},
        {'indice': 14, 'doublons': user.cards.count(14), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Fulbert Latrouille', 'description': "1014 - 1097. Ne sortit de sa maison que lorsqu'un sortilège fit s'écrouler son toit."},
        {'indice': 15, 'doublons': user.cards.count(15), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Paracelse', 'description': '1493 - 1541. Contemporain de Copernic et de Léonard de Vinci, médecin génial dont les théories audacieuses contestaient la pensée médiévale. On lui attribue la découverte du Fourchelang.'},
        {'indice': 16, 'doublons': user.cards.count(16), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Cliodna', 'description': 'Moyen Âge, dates inconnues. Druidesse irlandaise ayant découvert les propriétés de la rosée de lune.'},
        {'indice': 17, 'doublons': user.cards.count(17), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Morgane', 'description': 'Moyen Âge, dates inconnues. Demi-sœur du Roi Arthur. Férue de magie noire, ennemie jurée de Merlin.'},
        {'indice': 18, 'doublons': user.cards.count(18), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Ulric le Follingue', 'description': "Moyen Âge, dates inconnues. Magicien très original, célèbre pour la méduse qu'il portait comme chapeau."},
        {'indice': 19, 'doublons': user.cards.count(19), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Norbert Dragonneau', 'description': "1897 - aujourd'hui. Auteur populaire de Vie et habitat des animaux fantastiques."},
        {'indice': 20, 'doublons': user.cards.count(20), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gwendoline la Fantasque', 'description': "Moyen Âge, dates inconnues. Aimait tant monter sur le bûcher qu'elle parvint à se faire capturer quatorze fois sous divers déguisements."},
        {'indice': 21, 'doublons': user.cards.count(21), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Stoddard Withers', 'description': '1672 - 1769. Éleveur de chevaux ailés.'},
        {'indice': 22, 'doublons': user.cards.count(22), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Circé', 'description': 'Grèce antique. Vécut dans la Grèce antique sur Aeaea, transforma des marins en cochons.'},
        {'indice': 23, 'doublons': user.cards.count(23), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Glenda Chittock', 'description': "1964 - aujourd'hui. Présente L'heure ensorcelante sur RITM (Radio Indépendante à Transmission Magique)."},
        {'indice': 24, 'doublons': user.cards.count(24), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Adalbert Lasornette', 'description': '1899 - 1981. Célèbre théoricien de la magie.'},
        {'indice': 25, 'doublons': user.cards.count(25), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Perpetua Fancourt', 'description': "1900 - 1991. Sorcière ayant inventé le Lunascope."},
        {'indice': 26, 'doublons': user.cards.count(26), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Almerick Sawbridge', 'description': "1602 - 1699. Célèbre pourfendeur d'un troll qui terrorisait ceux qui traversaient la Wye. Le troll en question aurait été l'un des plus imposants de toute la Grande-Bretagne, avec un poids d'une tonne."},
        {'indice': 27, 'doublons': user.cards.count(27), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Mirabella Plunkett', 'description': "1839 - date inconnue. Célèbre pour être tombée amoureuse d'un triton au Loch Lomond alors qu'elle était en vacances. Lorsque ses parents lui interdirent de se marier, elle se transforma en crevette et ne réapparut jamais."},
        {'indice': 28, 'doublons': user.cards.count(28), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Tilly Toke', 'description': "1903 - 1991. Obtint l'Ordre de Merlin, première classe pour avoir sauvé de nombreux non magiciens lors de l'incident d'Ilfracombe en 1932, quand un dragon fonça sur une foule de baigneurs."},
        {'indice': 29, 'doublons': user.cards.count(29), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Archibald Alderton', 'description': "1568 - 1623. Fit sauter le hameau de Lagoutte dans le Hampshire en confectionnant un gâteau d'anniversaire."},
        {'indice': 30, 'doublons': user.cards.count(30), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Artemisia Lufkin', 'description': '1754 - 1825. Première sorcière à devenir ministre de la Magie.'},
        {'indice': 31, 'doublons': user.cards.count(31), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Balfour Blane', 'description': "1566 - 1629. Fondateur de la Commission des sortilèges expérimentaux."},
        {'indice': 32, 'doublons': user.cards.count(32), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Brigitte Wenlock', 'description': "1202 - 1285. Première arithmancienne à prouver les propriétés magiques du chiffre sept."},
        {'indice': 33, 'doublons': user.cards.count(33), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Beaumont Marjoribanks', 'description': "1742 - 1845. Pionnier de la botanique et collectionneur de plantes rares. Découvrit la Branchiflore."},
        {'indice': 34, 'doublons': user.cards.count(34), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Donaghan Tremlett', 'description': "1972 - aujourd'hui. Joue de la basse dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 35, 'doublons': user.cards.count(35), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Bowman Wright', 'description': "1492 - 1560. Célèbre pour avoir élaboré le Vif d'or."},
        {'indice': 36, 'doublons': user.cards.count(36), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Jocelyn Wadcock', 'description': "1911 - aujourd'hui. Poursuiveur de l'équipe de Quidditch de Flaquemare. Détient le record du plus grand nombre de buts inscrits en une saison en Grande-Bretagne au cours de ce siècle (lors du match contre les Chauves-Souris de Fichucastel)."},
        {'indice': 37, 'doublons': user.cards.count(37), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Cassandra Vablatsky', 'description': "1894 - 1997. Voyante célèbre, auteur de Lever le voile du futur."},
        {'indice': 38, 'doublons': user.cards.count(38), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Chauncey Oldridge', 'description': '1342 - 1379. Première victime connue de la varicelle du dragon.'},
        {'indice': 39, 'doublons': user.cards.count(39), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gwenog Jones', 'description': "1968 - aujourd'hui. Capitaine de la première équipe féminine de Quidditch, les Holyhead Harpies."},
        {'indice': 40, 'doublons': user.cards.count(40), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Carlotta Pinkstone', 'description': "1922 - aujourd'hui. Fit campagne pour annuler le code du secret établi par la Confédération internationale des mages et sorciers et révéler aux non magiciens l'existence des magiciens. Mademoiselle Pinkstone fut emprisonnée plusieurs fois pour son utilisation délibérée de la magie dans des lieux publics."},
        {'indice': 41, 'doublons': user.cards.count(41), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Godric Gryffondor', 'description': "Moyen Âge, dates inconnues. Co-fondateur de Poudlard. Donna son nom à l'une des maisons de l'école."},
        {'indice': 42, 'doublons': user.cards.count(42), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Crispin Cronk', 'description': '1795 - 1872. Fit un séjour à Azkaban pour avoir caché des sphinx dans son potager.'},
        {'indice': 43, 'doublons': user.cards.count(43), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Cyprien Youdle', 'description': "1312 - 1357. Seul arbitre de Quidditch ayant trouvé la mort au cours d'un match. Le lanceur du sortilège ne fut jamais pris mais la rumeur veut qu'il ait fait partie du public."},
        {'indice': 44, 'doublons': user.cards.count(44), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Devlin Corneblanche', 'description': "1945 - aujourd'hui. Fondateur de la Société des Balais de Course Nimbus."},
        {'indice': 45, 'doublons': user.cards.count(45), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Dunbar Oglethorpe', 'description': "1968 - aujourd'hui. Chef de l'UQAALEGB (Union de Quidditch pour l'Administration et l'Amélioration de la Ligue et des Efforts de Grande-Bretagne)."},
        {'indice': 46, 'doublons': user.cards.count(46), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Miranda Fauconnette', 'description': "1921 - aujourd'hui. Célèbre pour avoir écrit un grimoire."},
        {'indice': 47, 'doublons': user.cards.count(47), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Edgar Stroulger', 'description': "1703 - 1798. Inventeur du Scrutoscope."},
        {'indice': 48, 'doublons': user.cards.count(48), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Salazar Serpentard', 'description': "Moyen Âge, dates inconnues. Co-fondateur de Poudlard. Donna son nom à l'une des maisons de l'école."},
        {'indice': 49, 'doublons': user.cards.count(49), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Elladora Ketteridge', 'description': "1656 - 1729. Découvrit l'utilité de la Branchiflore lorsqu'elle faillit s'étouffer en l'avalant et ne fut soulagée qu'en plongeant la tête dans un seau d'eau."},
        {'indice': 50, 'doublons': user.cards.count(50), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Musidora Barkwith', 'description': "1520 - 1666. Compositeur de la Suite enchantée, œuvre inachevée, avec tuba explosif. L'œuvre est interdite depuis sa dernière présentation en 1902, date à laquelle elle fit sauter le toit de la mairie d'Ackerley."},
        {'indice': 51, 'doublons': user.cards.count(51), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Ethelred Toujourprêt', 'description': "Moyen Âge, dates inconnues. Célèbre pour se vexer pour un rien et pour maudire d'innocents passants. Mourut en prison."},
        {'indice': 52, 'doublons': user.cards.count(52), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Félix Labeille', 'description': "1447 - 1508. Inventeur du sortilège d'Allégresse."},
        {'indice': 53, 'doublons': user.cards.count(53), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Greta Grandamour', 'description': "1960 - aujourd'hui. Auteur de Comment ensorceler votre fromage."},
        {'indice': 54, 'doublons': user.cards.count(54), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gaspard Shingleton', 'description': "1959 - aujourd'hui. Inventeur du célèbre chaudron à touillage automatique."},
        {'indice': 55, 'doublons': user.cards.count(55), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Honoria Nutcombe', 'description': '1665 - 1743. fonda la Société pour la mise au rebut des vieilles sorcières.'},
        {'indice': 56, 'doublons': user.cards.count(56), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gédéon Miette', 'description': "1975 - aujourd'hui. Joueur de biniou dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 57, 'doublons': user.cards.count(57), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gifford Ollerton', 'description': "1390 - 1441. Célèbre pourfendeur de géants. Tua le géant Hengist de Barnton."},
        {'indice': 58, 'doublons': user.cards.count(58), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Glover Hipworth', 'description': "1742 - 1805. Inventeur de la Pimentine, qui soigne la grippe."},
        {'indice': 59, 'doublons': user.cards.count(59), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gregory le Hautain', 'description': "Moyen Âge, dates inconnues. Célèbre inventeur de la pommade pommadante Grégoire, une potion persuadant celui qui l'utilise que celui qui la lui a offerte est son meilleur ami. Aurait ainsi infiltré la cour du Roi Arthur et aurait fait fortune."},
        {'indice': 60, 'doublons': user.cards.count(60), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Laverne de Montmorency', 'description': "1823 - 1893. Créa de nombreux philtres d'amour."},
        {'indice': 61, 'doublons': user.cards.count(61), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Havelock Sweeting', 'description': "1634 - 1710. Spécialiste des licornes. Créa de nombreuses réserves de licornes en Grande-Bretagne."},
        {'indice': 62, 'doublons': user.cards.count(62), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Ignatia Wildsmith', 'description': '1227 - 1320. Sorcière qui inventa la poudre de cheminette.'},
        {'indice': 63, 'doublons': user.cards.count(63), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Herman Wintringham', 'description': "1974 - aujourd'hui. Joue du luth dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 64, 'doublons': user.cards.count(64), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Jocunda Sykes', 'description': "1915 - aujourd'hui. Première personne à traverser l'Atlantique sur un balai."},
        {'indice': 65, 'doublons': user.cards.count(65), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Gondoline Oliphant', 'description': "1720 - 1799. Spécialiste des trolls. Victime de son modèle lors d'une séance de pose."},
        {'indice': 66, 'doublons': user.cards.count(66), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Flavius Belby', 'description': "1715 - 1791. Seul magicien capable de survivre à une attaque de yétis."},
        {'indice': 67, 'doublons': user.cards.count(67), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Justus Pilliwickle', 'description': "1862 - 1953. Célèbre chef du Département de la justice magique."},
        {'indice': 68, 'doublons': user.cards.count(68), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Kirley Duke', 'description': "1971 - aujourd'hui. Guitariste solo dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 69, 'doublons': user.cards.count(69), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Bertie Crochue', 'description': "1935 - aujourd'hui. Inventa la recette des Dragées surprises de Bertie Crochue."},
        {'indice': 70, 'doublons': user.cards.count(70), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Léopoldine Smethwyck', 'description': '1829 - 1910. Première sorcière anglaise à arbitrer un match de Quidditch.'},
        {'indice': 71, 'doublons': user.cards.count(71), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Reine Maëva', 'description': "Sorcière légendaire ayant formé de jeunes sorciers en Irlande avant l'ouverture de Poudlard, école de sorcellerie."},
        {'indice': 72, 'doublons': user.cards.count(72), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Helga Poufsouffle', 'description': "Moyen Âge, dates inconnues. Co-fondatrice de Poudlard. Donna son nom à l'une des maisons de l'école."},
        {'indice': 73, 'doublons': user.cards.count(73), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Mopsus', 'description': "Grèce antique. Devin des temps anciens, vainqueur de Calchas lors d'un concours d'augures."},
        {'indice': 74, 'doublons': user.cards.count(74), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Montague Knightley', 'description': "1506 - 1588. Champion d'échecs magiques."},
        {'indice': 75, 'doublons': user.cards.count(75), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Mungo Bonham', 'description': "1560 - 1659. Fondateur de l'hôpital Saint-Mungo pour traitements et blessures magiques."},
        {'indice': 76, 'doublons': user.cards.count(76), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Myron Wagtail', 'description': "1970 - aujourd'hui. Chante dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 77, 'doublons': user.cards.count(77), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Norvel Twonk', 'description': "1888 - 1957. Mourut en essayant de sauver un enfant non magicien d'une Manticore. Fut nommé Commandeur du Grand-Ordre de Merlin à titre posthume."},
        {'indice': 78, 'doublons': user.cards.count(78), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Orsino Thruston', 'description': "1976 - aujourd'hui. Joue de la batterie dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 79, 'doublons': user.cards.count(79), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Oswald Beamish', 'description': '1850 - 1932. Pionnier dans la lutte pour les droits des gobelins.'},
        {'indice': 80, 'doublons': user.cards.count(80), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Béatrice Bloxam', 'description': "1794 - 1810. Auteur des Contes des Crottes du Crapaud, interdits car causant des nausées."},
        {'indice': 81, 'doublons': user.cards.count(81), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Quong Po', 'description': "1443 - 1539. Magicien chinois ayant découvert l'usage des œufs de cent ans explosifs."},
        {'indice': 82, 'doublons': user.cards.count(82), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Rowena Serdaigle', 'description': "Moyen Âge, dates inconnues. Co-fondatrice de Poudlard. Donna son nom à l'une des maisons de l'école."},
        {'indice': 83, 'doublons': user.cards.count(83), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Rodrigue Plumpton', 'description': "1889 - 1987. Attrapeur de l'équipe de Quidditch de Grande-Bretagne. Détient le record du rattrapage de Vif d'or, en trois secondes et demie."},
        {'indice': 84, 'doublons': user.cards.count(84), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Roland Tonneau', 'description': "1903 - aujourd'hui. Actuel président de l'équipe de Quidditch de Grande-Bretagne."},
        {'indice': 85, 'doublons': user.cards.count(85), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Blenheim Stalk', 'description': "1920 - aujourd'hui. Spécialiste des non magiciens, qui écrivit, entre autres œuvres, Les non magiciens qui nous voient."},
        {'indice': 86, 'doublons': user.cards.count(86), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Dorcas Bienaimée', 'description': "1812 - 1904. Fonda la Société des Sorcières en Détresse."},
        {'indice': 87, 'doublons': user.cards.count(87), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Thadée Thurkell', 'description': '1632 - 1692. Célèbre pour avoir eu sept fils satires et pour les avoir tous transformés en hérissons.'},
        {'indice': 88, 'doublons': user.cards.count(88), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Célestina Moldubec', 'description': "1917 - aujourd'hui. Célèbre chanteuse populaire."},
        {'indice': 89, 'doublons': user.cards.count(89), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Alberta Toothill', 'description': "1391 - 1483. remporta la compétition mondiale des duels de sorciers en 1430. Célèbre pour avoir vaincu le favori, Samson Wiblin, avec un sortilège d'explosion."},
        {'indice': 90, 'doublons': user.cards.count(90), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Sacharissa Tugwood', 'description': '1874 - 1966. Pionnière des potions de beauté. Découvrit les propriétés curatives des pustules de Bubobulbs.'},
        {'indice': 91, 'doublons': user.cards.count(91), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Wilfred Elphick', 'description': "1112 - 1199. Premier sorcier à être saigné à mort par un étrompard d'Afrique."},
        {'indice': 92, 'doublons': user.cards.count(92), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Xavier Rastrick', 'description': "1750 - 1836. Célèbre magicien animateur ayant brusquement disparu à tout jamais en dansant le tango au milieu d'une foule de trois cents personnes à Painswick."},
        {'indice': 93, 'doublons': user.cards.count(93), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Heathcote Barbary', 'description': "1974 - aujourd'hui. Guitariste dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 94, 'doublons': user.cards.count(94), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Merton Graves', 'description': "1978 - aujourd'hui. Violoncelliste dans le célèbre groupe Bizarr' Sisters."},
        {'indice': 95, 'doublons': user.cards.count(95), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Yardley Platt', 'description': "1446 - 1557. Tueur de gobelins en série."},
        {'indice': 96, 'doublons': user.cards.count(96), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Hengist de Woodcroft', 'description': "Moyen Âge, dates inconnues. Chassé de son domicile par des persécuteurs non magiciens, Hengist se serait installé en Écosse où il fonda Pré-au-Lard. Les Trois Balais seraient son ancienne demeure."},
        {'indice': 97, 'doublons': user.cards.count(97), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Alberic Grunnion', 'description': '1803 - 1882. Inventeur de la Bombabouse.'},
        {'indice': 98, 'doublons': user.cards.count(98), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Dymphna Furmage', 'description': "Victime d'un enlèvement par des farfadets lors de ses vacances en Cornouailles et célèbre pour avoir vécu dans la terreur depuis. Tenta de décider le ministère de la Magie à tuer les farfadets avec douceur."},
        {'indice': 99, 'doublons': user.cards.count(99), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Daisy Dodderidge', 'description': '1467 - 1555. Première propriétaire du Chaudron Baveur.'},
        {'indice': 100, 'doublons': user.cards.count(100), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Harry Potter', 'description': 'Le Survivant.'},
        {'indice': 101, 'doublons': user.cards.count(101), 'url': url_for('routes.to_encyclopedie', theme='1. Les Personnages', chapitre='a. Les Personnages Principaux', nom='Harry Potter') + '#section-3', 'noms': 'Albus Dumbledore', 'description': 'Directeur de Poudlard.'}
    ]

    return render_template("pages/jeux/album.html", username=user.username, user=user, cards=cards, carte_favorite=carte_favorite)

@routes_bp.route("/quiz/<mode>/<name>/<int:index>", methods=["GET", "POST"])
def quiz(mode, name, index):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user = User.query.get(session['user_id'])

    # --- quizzes ---

    if mode == 'express':
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        if not progress:
            progress = Progress(user_id=user.id, quiz_name=name, best_score=0)
            db.session.add(progress)
            db.session.commit()

        meilleur_score = progress.best_score

        quiz_data = get_quiz_by_name(name)
        if not quiz_data:
            return "Quiz introuvable", 404

        total_questions = len(quiz_data['questions'])

        if 'quiz_answers' not in session:
            session['quiz_answers'] = {}

        mode_express = request.args.get('mode_express', 'question')

        if request.method == "POST":
            if mode_express == "question":
         
                answer = request.form.get('answer')
                session['quiz_answers'][str(index)] = answer
                session['explanation'] = quiz_data['questions'][index]['explanation']
                session.modified = True

                return redirect(url_for('routes.quiz', mode=mode, name=name, index=index, mode_express='correction'))

            elif mode_express == "correction":
             
                if index + 1 < total_questions:
                    return redirect(url_for('routes.quiz', mode=mode, name=name, index=index+1))
                else:
                    score = 0
                    for i in range(total_questions):
                        if session['quiz_answers'].get(str(i)) == quiz_data['questions'][i]['answer']:
                            score += 1
                    session.pop('quiz_answers')  
                    session['quiz_score'] = score
                    return redirect(url_for('routes.quiz_end', mode=mode, name=name))
                
        question = quiz_data['questions'][index]
        is_last = (index == total_questions - 1)
        explication = session.get('explanation', '')

        correct_answer = question.get('answer')
        answer = session.get('quiz_answers', {}).get(str(index))

        if answer == correct_answer:
            message = "Bonne réponse !"
            statut = "success"
        else:
            message = "Mauvaise réponse !"
            statut = "error"

        return render_template(
            "pages/jeux/quiz.html",
            username=user.username,
            user=user,
            quiz=quiz_data,
            question=question,
            index=index,
            is_last=is_last,
            best_score=meilleur_score,
            mode=mode,
            mode_express=mode_express,
            explication=explication,
            answer=correct_answer,
            message=message,
            statut=statut
        )

    elif mode == 'choixpeau':
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        if not progress:
            progress = Progress(user_id=user.id, quiz_name=name, maison="")
            db.session.add(progress)
            db.session.commit()

        maison_final = progress.maison

        quiz_data = get_quiz_by_name(name)
        if not quiz_data:
            return "Quiz introuvable", 404

        total_questions = len(quiz_data['questions'])

        if 'quiz_answers' not in session:
            session['quiz_answers'] = {}

        if request.method == "POST":
            answer_index = request.form.get('answer')
            session['quiz_answers'][str(index)] = answer_index
            session.modified = True

            if index + 1 < total_questions:
                return redirect(url_for("routes.quiz", mode=mode, name=name, index=index+1))
            
            else:
                maison_scores = {'Gryffondor' : 0, "Poufsouffle" : 0, "Serdaigle" : 0, "Serpentard" : 0}

                for i in range(total_questions): 
                    q_data = quiz_data['questions'][i]
                    choix_index = session['quiz_answers'].get(str(i))

                    if choix_index is not None:
                        choix_index = int(choix_index)

                        if len(q_data['options']) == 4:
                            nom_maison = q_data['answer'][choix_index]
                            maison_scores[nom_maison] += 1

                        elif len(q_data['options']) == 2:
                            if choix_index == 0:
                                maison_scores[q_data['answer'][0]] += 1
                                maison_scores[q_data['answer'][1]] += 1
                            else:
                                maison_scores[q_data['answer'][2]] += 1
                                maison_scores[q_data['answer'][3]] += 1
                
                maximum = max(maison_scores.values())
                tab_maison = []
                for cle in maison_scores:
                    if maison_scores[cle] == maximum:
                        tab_maison.append(cle)
                if len(tab_maison) > 1:
                    from random import choice
                    final = choice(tab_maison)
                else:
                    final = tab_maison[0]

                progress.maison = final
                db.session.commit()

                session.pop('quiz_answers')
                session.pop('maison_final', None)

                return redirect(url_for('routes.quiz_end', name=name, mode=mode))
            
        question = quiz_data['questions'][index]
        is_last = (index == total_questions - 1)
            
        return render_template("pages/jeux/quiz.html", username=user.username, user=user, quiz=quiz_data, index=index, question=question, is_last=is_last, maison_final=maison_final, mode=mode)
    
    elif mode == 'alignement':
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        if not progress:
            progress = Progress(user_id=user.id, quiz_name=name, alignement="")
            db.session.add(progress)
            db.session.commit()

        alignement_final = progress.alignement

        quiz_data = get_quiz_by_name(name)
        if not quiz_data:
            return "Quiz introuvable", 404

        total_questions = len(quiz_data['questions'])

        if 'quiz_answers' not in session:
            session['quiz_answers'] = {}

        if request.method == "POST":
            answer_index = request.form.get('answer')
            session['quiz_answers'][str(index)] = answer_index
            session.modified = True

            if index + 1 < total_questions:
                return redirect(url_for("routes.quiz", mode=mode, name=name, index=index+1))
            
            else:
                alignement = 0

                for i in range(total_questions): 
                    q_data = quiz_data['questions'][i]
                    index_choix = session['quiz_answers'].get(str(i))

                    if index_choix is not None:
                        index_choix = int(index_choix)
                        choix = q_data['answer'][index_choix]

                        if choix == "mauvais":
                            alignement += 1
                
                if alignement == 0:
                    final = "Luna Lovegood"
                elif 1 <= alignement <= 6:
                    final = "Lumière"
                elif alignement == 7:
                    final = "Neutre"
                elif 8 <= alignement <= 14:
                    final = "Ombre"
                else: 
                    final = "Voldemort"

                progress.alignement = final
                db.session.commit()

                session.pop('quiz_answers')
                session.pop('alignement_final', None)

                return redirect(url_for('routes.quiz_end', name=name, mode=mode))
            
        question = quiz_data['questions'][index]
        is_last = (index == total_questions - 1)
            
        return render_template("pages/jeux/quiz.html", username=user.username, user=user, quiz=quiz_data, index=index, question=question, is_last=is_last, alignement_final=alignement_final, mode=mode)

    elif mode == 'patronus':
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        if not progress:
            progress = Progress(user_id=user.id, quiz_name=name, patronus="")
            db.session.add(progress)
            db.session.commit()

        patronus_final = progress.patronus
        
        quiz_data = get_quiz_by_name(name)
        if not quiz_data:
            return "Quiz introuvable", 404

        total_questions = len(quiz_data['questions'])

        if 'quiz_answers' not in session:
            session['quiz_answers'] = {}

        if request.method == "POST":
            answer = request.form.get('answer')
            session['quiz_answers'][str(index)] = answer
            session.modified = True

            if index + 1 < total_questions:
                return redirect(url_for("routes.quiz", mode=mode, name=name, index=index+1))
            
            else:
                patronus = {"Abraxan" : 0, "Aigle" : 0, "Albatros hurleur" : 0, "Alezans" : 0,"Autour des palombes" : 0, "Balbuzard Pêcheur" : 0, "Barzoïs" : 0, "Basset Hound" : 0, "Bâtard" : 0, "Beagle" : 0, "Belette" : 0, "Biche" : 0, "Blaireau" : 0, "Bleu-Russe" : 0, "Buffle" : 0, "Busard des Marais" : 0, "Buse" : 0, "Campagnol" : 0, "Capucin" : 0, "Cerf" : 0, "Chat Calico" : 0, "Chat Écaille-de-tortue" : 0, "Chat Noir et Blanc" : 0, "Chat Roux" : 0, "Chat Sauvage" : 0, "Chauve-Souris" : 0, "Chevaux Bais" : 0, "Chevaux Blancs" : 0, "Chevaux Dun" : 0, "Chevaux Gris Pommelés" : 0, "Chevaux Noirs" : 0, "Chevaux Pinto" : 0, "Chevêche d’Athéna" : 0, "Chien de St-Hubert" : 0, "Chouette lapone" : 0, "Chow-chow" : 0, "Cobra Royal" : 0, "Colibri" : 0, "Corbeau" : 0, "Corneille" : 0, "Couleuvre" : 0, "Crotale" : 0, "Cygne Blanc" : 0, "Cygne Noir" : 0, "Dauphin" : 0, "Deerhound" : 0, "Dragon" : 0, "Écureuil Gris" : 0, "Écureuil Roux" : 0, "Éléphant" : 0, "Épervier" : 0, "Eruptif" : 0, "Faisan" : 0, "Faucon" : 0, "Fox-Terrier" : 0, "Granian" : 0, "Guépard" : 0, "Harfang des Neiges" : 0, "Hérisson" : 0, "Hermine" : 0, "Héron" : 0, "Hibou brun" : 0, "Hibou Grand Duc" : 0, "Hippogriffe" : 0, "Hirondelle" : 0, "Husky" : 0, "Hyène" : 0, "Impala" : 0, "Irish Wolfhound" : 0, "Lapin sauvage" : 0, "Léopard" : 0, "Lévrier" : 0, "Libellule" : 0, "Licorne" : 0, "Lièvre Brun" : 0, "Lièvre des Montagnes" : 0, "Lion" : 0, "Lionne" : 0, "Loup" : 0, "Loutre" : 0, "Lynx" : 0, "Mamba Noir" : 0, "Manx" : 0, "Martin-Pêcheur" : 0, "Martinet" : 0, "Martre des Pins" : 0, "Mastiff" : 0, "Merle Noir" : 0, "Moineau" : 0, "Musaraigne" : 0, "Nightjar" : 0, "Nebelung" : 0, "Occamy" : 0, "Ocicat" : 0, "Orang-Outan" : 0, "Orque" : 0, "Oryctérope du Cap" : 0, "Oryx" : 0, "Otus" : 0, "Ours Brun" : 0, "Ours Noir" : 0, "Ours Polaire" : 0, "Paon" : 0, "Phénix" : 0, "Phoque" : 0, "Pie" : 0, "Podenco d’Ibiza" : 0, "Putois" : 0, "Python" : 0, "Ragdoll" : 0, "Rat" : 0, "Renard" : 0, "Requin" : 0, "Rhinocéros" : 0, "Rottweiler" : 0, "Rouge-Gorge" : 0, "Runespoor" : 0, "Salamandre" : 0, "Salamandre de feu" : 0, "Sanglier" : 0, "Saumon" : 0, "Sibérien" : 0, "Sombral" : 0, "Souris des bois" : 0, "Souris des champs" : 0, "Sphynx" : 0, "St-Bernard" : 0, "Taupe" : 0, "Terre-Neuve" : 0, "Tigre" : 0, "Tigresse" : 0, "Tonkinois" : 0, "Vautour" : 0, "Vison" : 0, "Vipère" : 0, "West Highland White Terrier" : 0 }
                for i in range(total_questions):
                    stored_value = session['quiz_answers'].get(str(i))
                    options = quiz_data["questions"][i]["options"]
                    try:
                        choix = options.index(stored_value)
                    except ValueError:
                        continue

                    answer_list = quiz_data["questions"][i]['answer'][choix]

                    for patro in answer_list:
                        patronus[patro] += 1
                
                maximum = max(patronus.values())
                tab_patronus = []
                for cle in patronus:
                    if patronus[cle] == maximum:
                        tab_patronus.append(cle)
                if len(tab_patronus) > 1:
                    from random import choice
                    final = choice(tab_patronus)
                else:
                    final = tab_patronus[0]

                progress.patronus = final
                db.session.commit()

                session.pop('quiz_answers', None)
                session.pop('patronus_final', None)

                return redirect(url_for('routes.quiz_end', name=name, mode=mode))
            
        question = quiz_data['questions'][index]
        is_last = (index == total_questions - 1)
            
        return render_template("pages/jeux/quiz.html", username=user.username, user=user, quiz=quiz_data, index=index, question=question, is_last=is_last, mode=mode, patronus_final=patronus_final)

    elif mode == 'matiere':
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        if not progress:
            progress = Progress(user_id=user.id, quiz_name=name, matiere="")
            db.session.add(progress)
            db.session.commit()

        matiere_final = progress.matiere

        quiz_data = get_quiz_by_name(name)
        if not quiz_data:
            return "Quiz introuvable", 404

        total_questions = len(quiz_data['questions'])

        if 'quiz_answers' not in session:
            session['quiz_answers'] = {}

        if request.method == "POST":
            answer_index = request.form.get('answer')
            session['quiz_answers'][str(index)] = answer_index
            session.modified = True

            if index + 1 < total_questions:
                return redirect(url_for("routes.quiz", mode=mode, name=name, index=index+1))
            
            else:
                matiere_scores = {'Alchimie' : 0, "Arithmancie" : 0, "Arithmancie avancée" : 0, "Art de la magie noire" : 0, "Astronomie" : 0, "Botanique" : 0, "Divination" : 0, "Défense contre les forces du Mal" : 0, "Étude des anciennes Runes" : 0, "Étude des goules" : 0, "Étude des Moldus" : 0, "Histoire de la magie" : 0, "Magie de la terre" : 0, "Métamorphose" : 0, "Potions" : 0, "Soins aux créatures magiques" : 0, "Sortilèges" : 0, "Théorie magique" : 0, "Vol" : 0, "Xylomancie" : 0}

                for i in range(total_questions): 
                    q_data = quiz_data['questions'][i]
                    choix_index = session['quiz_answers'].get(str(i))

                    if choix_index is not None:
                        choix_index = int(choix_index)

                        nom_matiere = q_data['answer'][choix_index]
                        matiere_scores[nom_matiere] += 1
                
                maximum = max(matiere_scores.values())
                tab_matiere = []
                for cle in matiere_scores:
                    if matiere_scores[cle] == maximum:
                        tab_matiere.append(cle)
                if len(tab_matiere) > 1:
                    from random import choice
                    final = choice(tab_matiere)
                else:
                    final = tab_matiere[0]

                progress.matiere = final
                db.session.commit()

                session.pop('quiz_answers')
                session.pop('matiere_final', None)

                return redirect(url_for('routes.quiz_end', name=name, mode=mode))
            
        question = quiz_data['questions'][index]
        is_last = (index == total_questions - 1)
            
        return render_template("pages/jeux/quiz.html", username=user.username, user=user, quiz=quiz_data, index=index, question=question, is_last=is_last, matiere_final=matiere_final, mode=mode)

    else:
        return 'quiz introuvable !', 404

@routes_bp.route("/quiz/<mode>/<name>/end")
def quiz_end(name, mode):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user = User.query.get(session['user_id'])

    maisons = {}
    for maison_name in ["Gryffondor", "Poufsouffle", "Serdaigle", "Serpentard"]:
        h = House.query.filter_by(name=maison_name).first()
        if not h:
            h = House(name=maison_name, points=0)
            db.session.add(h)
            db.session.commit() 
        maisons[maison_name] = h

    user_progress = Progress.query.filter_by(user_id=user.id, quiz_name="points_perso").first()
    if not user_progress:
        user_progress = Progress(user_id=user.id, quiz_name="points_perso", points_perso=0)
        db.session.add(user_progress)
        db.session.commit()
    points = user_progress.points_perso

    progress_maison = Progress.query.filter_by(user_id=user.id, quiz_name="maison").first()
    if not progress_maison:
        progress_maison = Progress(user_id=user.id, quiz_name="maison", maison="")
        db.session.add(progress_maison)
        db.session.commit()
    maison = progress_maison.maison

    # --- Mode EXPRESS --- #
    if mode in ['express']:
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        if not progress:
            progress = Progress(user_id=user.id, quiz_name=name, best_score=0)
            db.session.add(progress)

        quiz_data = get_quiz_by_name(name)
        score = session.pop('quiz_score', 0)  
        total = len(quiz_data['questions'])

        if score > progress.best_score:
            progress.best_score = score

        points += score
        user_progress.points_perso = points   
        db.session.commit()

        if maison in maisons:
            maisons[maison].points += score
        else:
            return "problème de maison", 404
        
        if score > total/2:
            message = "Bravo"
        else: 
            message = "Dommage"

        db.session.commit() 

        return render_template(
            "pages/jeux/quiz_end.html",
            username=user.username,
            user=user,
            quiz=quiz_data,
            score=score,
            total=total,
            message=message,
            best_score=progress.best_score,
            mode=mode,
            points=points,
            points_gryff=maisons["Gryffondor"].points,
            points_pouf=maisons["Poufsouffle"].points,
            points_serd=maisons["Serdaigle"].points,
            points_serp=maisons["Serpentard"].points
        )

    # --- Mode choixpeau --- #
    elif mode == 'choixpeau':
        quiz_data = get_quiz_by_name(name)
        progress_maison = Progress.query.filter_by(user_id=user.id, quiz_name="maison").first()
        maison = progress_maison.maison if progress_maison else ""

        desc_maisons = maisons_description['maisons_description'].get(maison, "Pas de description")

        return render_template(
            "pages/jeux/quiz_end.html",
            username=user.username,
            user=user,
            quiz=quiz_data,
            maison=maison,
            mode=mode,
            desc_maisons=desc_maisons
        )

    # --- Mode patronus --- #
    elif mode == 'patronus':
        quiz_data = get_quiz_by_name(name)
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        patronus = progress.patronus if progress else ""

        desc_patronus = patronus_description['patronus_descripton'].get(patronus, "Pas de description")

        return render_template(
            "pages/jeux/quiz_end.html",
            username=user.username,
            user=user,
            quiz=quiz_data,
            patronus=patronus,
            mode=mode,
            desc_patronus=desc_patronus
        )
    
    # --- Mode Alignement --- #
    elif mode == 'alignement':
        quiz_data = get_quiz_by_name(name)
        progress = Progress.query.filter_by(user_id=user.id, quiz_name=name).first()
        alignement = progress.alignement if progress else ""

        desc_alignement = alignement_description['alignement_description'].get(alignement, "Pas de description")

        return render_template(
            "pages/jeux/quiz_end.html",
            username=user.username,
            user=user,
            quiz=quiz_data,
            alignement=alignement,
            mode=mode,
            desc_alignement=desc_alignement
        )

    elif mode == 'matiere':
        quiz_data = get_quiz_by_name(name)
        progress_matiere = Progress.query.filter_by(user_id=user.id, quiz_name="matiere").first()
        matiere = progress_matiere.matiere if progress_matiere else ""

        desc_matiere = matiere_description['matiere_description'].get(matiere, "Pas de description")

        return render_template(
            "pages/jeux/quiz_end.html",
            username=user.username,
            user=user,
            quiz=quiz_data,
            matiere=matiere,
            mode=mode,
            desc_matiere=desc_matiere
        )

    else:
        return 'erreur', 404

@routes_bp.route('/set_carte_favorite', methods=['POST'])
def set_carte_favorite():
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403

    user = User.query.get(session['user_id'])
    data = request.get_json()
    carte = data.get("carte")
    favorite = data.get("favorite")

    if favorite:
        user.carte = str(carte)
    else:
        user.carte = ""

    db.session.commit()
    return jsonify({"status": "ok"})

# ----------------------------------------------------------- #
# --- Routes de redirection vers les pages (avec session) --- #
# ----------------------------------------------------------- #

@routes_bp.route("/")
def to_welcome():
    if 'user_id' in session:
        return redirect(url_for('routes.logout'))
    else:
        return render_template('index/index.html')

@routes_bp.route('/home')
def to_home():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    return render_template("home.html", username=user.username, user=user)

@routes_bp.route('/films')
def to_films():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    return render_template("pages/films.html", username=user.username, user=user)

@routes_bp.route('/livres')
def to_livres():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    return render_template("pages/livres.html", username=user.username, user=user)

@routes_bp.route('/encyclopedie')
def to_encyclopedie():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user = User.query.get(session['user_id'])
    profil_picture = user.profil_picture if user.profil_picture else "default.png"

    return render_template("pages/encyclopedie.html", username=user.username, user=user, profil_picture=profil_picture)

@routes_bp.route('/informations')
def to_informations():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    return render_template("pages/informations.html", username=user.username, user=user)

@routes_bp.route('/contact', methods = ["GET", "POST"])
def to_contact():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    return render_template("pages/contact.html", username=user.username, user=user)

@routes_bp.route('/admin_redirect')
def to_admin():
    if 'user_id' not in session:
        return redirect(url_for('routes_bp.login'))  

    user = User.query.get(session['user_id'])
    
    if user.admin == 1:
        return redirect('/admin')
    else:
        return render_template("admin/admin-only.html", username=user.username, user=user)

@routes_bp.route('/admin-only')
def admin_only():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template("admin/admin-only.html", username=user.username if user else None, user=user)

@routes_bp.route('/contacts', methods = ["POST"])
def contact():
    from app import mail

    mail = current_app.extensions['mail']

    nom = request.form['nom_utilisateur']
    user_mail = request.form['email_utilisateur']
    objet = request.form['objet']
    message = request.form['message']

    msg_admin = Message(
        subject = f'Nouveau message : {objet}', 
        sender=current_app.config['MAIL_USERNAME'], 
        recipients=['chrisaboukaram@gmail.com'], 
        reply_to=user_mail)
    
    msg_user = Message(
        subject='Confirmation de réception', 
        sender=current_app.config['MAIL_USERNAME'], 
        recipients=[user_mail])
    
    msg_user.html = render_template('pages/email/email_user.html', nom=nom, message=message, objet=objet)
    msg_admin.html = render_template('pages/email/email_admin.html', nom=nom, user_mail=user_mail, message=message, objet=objet)

    try :
        mail.send(msg_admin)
        mail.send(msg_user)
    except Exception as e:
        print("Erreur lors de l'envoi du mail de confirmation !")
        
    return redirect(url_for('routes.to_contact'))

@routes_bp.route('/logout')
def logout():
    resp = redirect(url_for('routes.login'))
    resp.set_cookie('localStorageKey', '', expires=0)
    session.clear()
    return redirect(url_for('routes.to_welcome'))

# -------------------- #
# --- Player vidéo --- #
# -------------------- #

@routes_bp.route('/player')
def player(): 
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    video_name = request.args.get('video')
    if not video_name:
        return "Vidéo non spécifiée", 400
    
    video_url = get_signed_url(video_name)
    
    film_favorite = (user.film == video_name)

    authorized = user.authorized
    
    films = {
        "harry_potter_un.mp4" : {
            "title" : "Harry Potter à l'école des sorcier",
            "year" : "2001",
            "description" : "Le jeune Harry découvre, le jour de ses 11 ans, qu’il est un sorcier. Il entre à Poudlard, une école de magie où il se lie d’amitié avec Ron et Hermione. Ensemble, ils découvrent les mystères qui entourent la pierre philosophale et le retour possible d’un certain Seigneur des Ténèbres...",
            "poster" : "1.webp",
        },

        "harry_potter_deux.mp4" : {
            "title" : "Harry Potter et la chambre des secrets",
            "year" : "2002",
            "description" : "De retour à Poudlard malgré les avertissements d’un elfe nommé Dobby, Harry fait face à une série d’attaques mystérieuses. Une chambre légendaire aurait été ouverte, libérant une créature terrifiante. Entre messages sanglants et secrets anciens, le danger rôde plus près qu’il ne le croit.",
            "poster" : "2.webp",
        },

        "harry_potter_trois.mp4" : {
            "title" : "Harry Potter et la prison d'azkaban",
            "year" : "2004",
            "description" : "Un dangereux évadé, Sirius Black, s’échappe de la prison d’Azkaban. Tout le monde pense qu’il cherche à tuer Harry. Mais les apparences sont trompeuses, et le jeune sorcier découvre des vérités bouleversantes sur son passé et sur la trahison de ses parents.",
            "poster" : "3.webp",
        },

        "harry_potter_quatre.mp4" : {
            "title" : "Harry Potter et la coupe de feu",
            "year" : "2005",
            "description" : "Harry est mystérieusement sélectionné pour participer au Tournoi des Trois Sorciers, une compétition dangereuse entre écoles de magie. Entre dragons, labyrinthes et maléfices, il réalise que le tournoi cache une sombre manœuvre : le retour de Voldemort est proche.",
            "poster" : "4.webp",
        },

        "harry_potter_cinq.mp4" : {
            "title" : "Harry Potter et l'ordre du phenix",
            "year" : "2007",
            "description" : "Alors que le ministère de la Magie refuse de croire au retour de Voldemort, Harry forme un groupe secret — “l’Armée de Dumbledore” — pour enseigner la défense à ses camarades. Mais la rébellion attire la colère d’une nouvelle ennemie redoutable : Dolores Ombrage.",
            "poster" : "5.webp",
        },

        "harry_potter_six.mp4" : {
            "title" : "Harry Potter et le prince de sang-mêler",
            "year" : "2009",
            "description" : "Dumbledore prépare Harry à affronter Voldemort en lui révélant les secrets de son passé. Tandis qu’un mystérieux manuel de potions appartenant au “Prince de sang-mêlé” intrigue Harry, l’ombre de la guerre s’étend sur Poudlard.",
            "poster" : "6.webp",
        },

        "harry_potter_sept.mp4" : {
            "title" : "Harry Potter et les reliques de la mort : partie 1",
            "year" : "2001",
            "description" : "Harry, Ron et Hermione quittent Poudlard pour détruire les Horcruxes, fragments de l’âme de Voldemort. En fuite, isolés et traqués, ils comprennent que la victoire aura un prix très lourd.",
            "poster" : "7.webp",
        },

        "harry_potter_huit.mp4" : {
            "title" : "Harry Potter et les reliques de la mort : partie 2",
            "year" : "2011",
            "description" : "La bataille finale fait rage à Poudlard. Harry doit affronter Voldemort une dernière fois pour sauver le monde des sorciers. Entre courage, amitié et sacrifice, l’histoire touche à sa fin… mais la légende commence.",
            "poster" : "8.webp",
        },

        "harry_potter_neuf.mp4" : {
            "title" : "Harry Potter 20ème aniversaire : retour à poudlard",
            "year" : "2022",
            "description" : "Pour célébrer les 20 ans du premier film, les acteurs principaux — Daniel Radcliffe, Emma Watson, Rupert Grint — et les réalisateurs se retrouvent à Poudlard. Ensemble, ils revivent les moments forts du tournage, partagent des souvenirs émouvants et rendent hommage à ceux qui ont marqué cette aventure magique. Un voyage plein de nostalgie et d’émotion pour tous les fans.",
            "poster" : "9.webp",
        },

        "les_animaux_fantastiques_un.mp4" : {
            "title" : "Les animaux fantastiques",
            "year" : "2016",
            "description" : "En 1926, le magizoologiste Norbert Dragonneau arrive à New York avec une valise pleine de créatures magiques. Lorsque certaines s’échappent, il doit les retrouver tout en évitant la menace d’un mage noir : Gellert Grindelwald. Une aventure magique au cœur de l’Amérique des années 1920.",
            "poster" : "10.webp",
        },

        "les_animaux_fantastiques_deux.mp4" : {
            "title" : "Les animaux fantastiques : les crimes de Grindelwald",
            "year" : "2018",
            "description" : "Grindelwald, désormais libre, rassemble des partisans pour instaurer la domination des sorciers sur les Moldus. Dumbledore fait appel à son ancien élève Norbert pour le stopper. Entre alliances et trahisons, la guerre des idées commence.",
            "poster" : "11.webp",
        },

        "les_animaux_fantastiques_trois.mp4" : {
            "title" : "Les animaux fantastiques : les secrets de Dumbledore",
            "year" : "2022",
            "description" : "Alors que Grindelwald gagne en puissance, Dumbledore forme une équipe pour contrecarrer ses plans. Mais un secret du passé lie les deux hommes… Un film plus intime, révélant les origines du combat entre le bien et le mal dans le monde des sorciers.",
            "poster" : "12.webp",
        },
    }

    film = films.get(video_name, {
        "title" : "film inconnu",
        "year" : "???",
        "description" : "Aucune informations disponible...",
        "poster" : "default.jpg" 
    })

    return render_template('pages/player/player.html', video=video_name, username=user.username, user=user, video_url=video_url, film_favorite=film_favorite, title=film["title"], year=film["year"], description=film["description"], poster=film["poster"], authorized=authorized)

@routes_bp.route('/progress', methods=['GET'])
def get_progress():
    uid = session.get('user_id'); vid = request.args['video']
    prog = Progress.query.filter_by(user_id=uid, video=vid).first()
    return jsonify(position=prog.position if prog else 0)

@routes_bp.route('/progress', methods=['POST'])
def set_progress():
    uid = session.get('user_id')
    vid = request.json['video']; pos = request.json['position']
    prog = Progress.query.filter_by(user_id=uid, video=vid).first()
    if not prog:
        prog = Progress(user_id=uid, video=vid, position=pos)
        db.session.add(prog)
    else:
        prog.position = pos
    db.session.commit()
    return '', 204

@routes_bp.route('/set_film_favorite', methods=['POST'])
def set_film_favorite():
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403

    user = User.query.get(session['user_id'])
    data = request.get_json()
    film = data.get("film")
    favorite = data.get("favorite")

    if favorite:
        user.film = film
    else:
        user.film = ""

    db.session.commit()
    return jsonify({"status": "ok"})

# -------------------- #
# --- Player book ---- #
# -------------------- #

@routes_bp.route('/book')
def book():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    book_name = request.args.get('book')
    if not book_name:
        return "Livre non spécifié", 400
    
    book_favorite = (user.livre == book_name)

    authorized = user.authorized
    
    books = ["1.pdf", "2.pdf", "3.pdf", "4.pdf", "5.pdf", "6.pdf", "7.pdf", "8.pdf", "9.pdf", "10.pdf", "11.pdf", "12.pdf", "13.pdf", "14.pdf"]

    if book_name not in books:
        book_name = "inconnu"

    return render_template('pages/player/book.html', book=book_name, username=user.username, user=user, book_favorite=book_favorite, authorized=authorized)

@routes_bp.route('/book_progress')
def get_book_progress():
    if 'user_id' not in session:
        return jsonify({"position": 1})  

    user_id = session['user_id']
    book = request.args.get("book")
    progress = Progress.query.filter_by(user_id=user_id, video=book).first()
    return jsonify({"position": progress.position if progress else 1})

@routes_bp.route('/book_progress', methods=['POST'])
def save_book_progress():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 403

    data = request.json
    book = data.get("book")
    page_num = data.get("pageNum")

    if not book or page_num is None:
        return jsonify({"error": "Invalid data"}), 400

    user_id = session['user_id']
    progress = Progress.query.filter_by(user_id=user_id, video=book).first()
    if not progress:
        progress = Progress(user_id=user_id, video=book, position=page_num)
        db.session.add(progress)
    else:
        progress.position = page_num

    db.session.commit()
    return jsonify({"success": True})

@routes_bp.route('/set_book_favorite', methods=['POST'])
def set_book_favorite():
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403

    user = User.query.get(session['user_id'])
    data = request.get_json()
    livre = data.get("book")
    favorite = data.get("favorite")

    if favorite:
        user.livre = livre
    else:
        user.livre = ""

    db.session.commit()
    return jsonify({"status": "ok"})

# healthcheck pour que la base de donnée soit toujours ouverte

@routes_bp.route('/healthcheck')
def healthcheck():
    try:
        from models import User
        User.query.limit(1).all()
        return "systeme outline", 200
    except Exception as e:
        return f"Database Offline : {str(e)}", 500