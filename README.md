# 🦉 Quibbler — Le site des fans de Harry Potter

Quibbler est une application web dédiée à l'univers Harry Potter. Elle propose des quiz, une encyclopédie, un système de cartes à collectionner, un lecteur de films, et bien plus encore — le tout avec un système de comptes utilisateurs et de maisons.

---

## ✨ Fonctionnalités

- **Quiz** — Teste tes connaissances sur les personnages, lieux, créatures, potions, sortilèges, gastronomie et bien d'autres thèmes
- **Patronus & Maison** — Découvre ta maison (Choixpeau) et ton patronus via des quiz dédiés
- **Encyclopédie** — Consulte une encyclopédie complète de l'univers Harry Potter
- **Films & Livres** — Accède à du contenu multimédia avec suivi de progression vidéo
- **Jeux & Cartes** — Ouvre des packs de cartes à collectionner et découvre des raretés
- **Album** — Consulte et organise ta collection de cartes
- **Profil utilisateur** — Personnalise ton compte avec une photo de profil, un animal favori, une carte favorite
- **Classement des maisons** — Un système de points par maison mis à jour en temps réel
- **Panel Admin** — Interface d'administration pour gérer les utilisateurs et les maisons

---

## 🛠️ Stack technique

| Technologie | Rôle |
|---|---|
| Python / Flask | Backend & routing |
| SQLAlchemy | ORM & gestion de la base de données |
| SQLite / PostgreSQL | Base de données (local / production) |
| Flask-Admin | Interface d'administration |
| Flask-Mail | Envoi d'emails (contact, notifications) |
| Cloudflare R2 / boto3 | Stockage des fichiers médias |
| Gunicorn | Serveur WSGI en production |
| Jinja2 | Templates HTML |

---

## 🚀 Installation locale

### Prérequis
- Python 3.10+
- pip

### Étapes

```bash
# 1. Clone le repo
git clone https://github.com/ChrisAkk/Quibbler.git
cd Quibbler

# 2. Installe les dépendances
pip install -r requirements.txt

# 3. Lance l'application
python app.py
```

L'application sera disponible sur `http://localhost:5001`

---

## ⚙️ Variables d'environnement

Crée un fichier `.env` à la racine avec les variables suivantes :

```env
SECRET_KEY=ta_cle_secrete
DATABASE_URL=sqlite:///quibbler.db   # ou une URL PostgreSQL en production
MAIL_PASSWORD=ton_mot_de_passe_mail
```

---

## 📁 Structure du projet

```
Quibbler/
├── app.py              # Point d'entrée de l'application
├── models.py           # Modèles de base de données (User, Progress, House)
├── routes.py           # Toutes les routes Flask
├── films.py            # Gestion du stockage Cloudflare R2
├── requirements.txt    # Dépendances Python
├── static/
│   ├── images/         # Images & assets visuels
│   ├── json/           # Données encyclopédie
│   └── favicon.png
└── templates/
    ├── base.html       # Template de base
    ├── home.html
    └── pages/          # Pages de l'application
```

---

## 🧙 Déploiement

L'application est configurée pour être déployée sur **Render** avec une base de données PostgreSQL (Neon). Le fichier `nixpacks.toml` est inclus pour la configuration automatique du build.

---

## 📬 Contact

Pour toute question, utilise le formulaire de contact disponible directement sur le site.