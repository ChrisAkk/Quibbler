from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

# ------------------ #
# --- Class User --- #
# ------------------ #

class User(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    admin          = db.Column(db.Integer, default = 0)
    authorized     = db.Column(db.Integer, default = 0)
    username       = db.Column(db.String(100), nullable=False)
    _password      = db.Column('password', db.String(255), nullable=False)
    profil_picture = db.Column(db.String(250), default="default.png")
    spark          = db.Column(db.Boolean, default=True)
    film           = db.Column(db.String(100), default="")
    livre          = db.Column(db.String(100), default="")
    carte          = db.Column(db.Integer, default=0)
    cards          = db.Column(MutableList.as_mutable(db.JSON), default=list)
    animal         = db.Column(db.String(100), default="")

    progresses     = db.relationship('Progress', backref='user', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError("Le mot de passe n'est pas accessible en clair")

    @password.setter
    def password(self, mot_de_passe_clair):
        self._password = generate_password_hash(mot_de_passe_clair)

    def check_password(self, mot_de_passe_clair):
        return check_password_hash(self._password, mot_de_passe_clair)

    def __repr__(self):
        return f'<User {self.id} - {self.username}>'

    
# ---------------------- #
# --- Class Progress --- #
# ---------------------- #

class Progress(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    video       = db.Column(db.String(255), nullable=True)
    position    = db.Column(db.Float, default=0.0)
    updated     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    best_score  = db.Column(db.Integer, default=0)
    quiz_name   = db.Column(db.String(255), nullable=True)
    maison      = db.Column(db.String(255), nullable=True, default="")
    patronus    = db.Column(db.String(255), nullable=True)
    alignement  = db.Column(db.String(255), nullable=True)
    matiere     = db.Column(db.String(255), nullable=True)
    points_perso = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'video'),
        db.UniqueConstraint('user_id', 'video'),
    )

    def __repr__(self):
        return f'<Progress user_id={self.user_id} video={self.video} quiz={self.quiz_name} position={self.position}>'

    
# -------------------- #
# --- Class Maison --- #
# -------------------- #

class House(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    name   = db.Column(db.String(50), unique=True, default="")
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<House {self.name} - {self.points}>'

