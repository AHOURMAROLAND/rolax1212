# ============================================================
#  frameworks.py — Détection et initialisation frameworks
#  rolax1212 v2.0.1 by Roland
# ============================================================

import subprocess
from pathlib import Path
from .ui import console, ok, info, warn, err, confirmer, separateur

# ============================================================
#  CATALOGUE
# ============================================================
FRAMEWORKS = {
    "django": {
        "nom": "Django", "langage": "Python", "version": "5.x",
        "couleur": "green", "icone": "🟢",
        "signatures": ["manage.py"],
        "install": "pip install django mysqlclient pillow python-decouple",
        "init_fn": "init_django",
        "fichiers_natifs": ["manage.py", "settings.py", "wsgi.py", "asgi.py",
                            "models.py", "views.py", "urls.py", "admin.py", "apps.py"],
        "notes": [
            "Utilise path() et non url()",
            "django-admin startproject pour créer le projet",
            "python manage.py startapp pour créer une app",
            "LoginRequiredMixin pour les class-based views",
            "AUTH_USER_MODEL pour un custom user",
            "python-decouple pour les variables d'environnement",
            "Chemins corrects : app/models.py, templates/app/page.html",
        ]
    },
    "fastapi": {
        "nom": "FastAPI", "langage": "Python", "version": "0.110+",
        "couleur": "cyan", "icone": "⚡",
        "signatures": [],
        "contenu_cles": ["from fastapi import", "FastAPI()", "APIRouter"],
        "install": "pip install fastapi uvicorn sqlalchemy pydantic python-dotenv",
        "init_fn": "init_fastapi",
        "fichiers_natifs": [],
        "notes": [
            "Utilise Annotated pour les dépendances",
            "async def pour les routes",
            "Pydantic v2 pour la validation",
            "APIRouter pour organiser les routes",
        ]
    },
    "flask": {
        "nom": "Flask", "langage": "Python", "version": "3.x",
        "couleur": "white", "icone": "🌶",
        "signatures": [],
        "contenu_cles": ["from flask import", "Flask(__name__)", "app.route"],
        "install": "pip install flask flask-sqlalchemy flask-login python-dotenv",
        "init_fn": "init_flask",
        "fichiers_natifs": [],
        "notes": [
            "Application factory pattern recommandé",
            "Blueprints pour organiser les routes",
            "flask-login pour l'authentification",
            "flask-migrate pour les migrations",
        ]
    },
    "laravel": {
        "nom": "Laravel", "langage": "PHP", "version": "11.x",
        "couleur": "red", "icone": "🔴",
        "signatures": ["artisan"],
        "install": "composer create-project laravel/laravel nom",
        "init_fn": "init_laravel",
        "fichiers_natifs": ["artisan", "routes/web.php", "routes/api.php"],
        "notes": [
            "php artisan make:model -mcr pour model+migration+controller",
            "Sanctum pour l'auth API",
            "Eloquent ORM pour la base de données",
            "Blade pour les templates",
            "php artisan serve pour lancer",
        ]
    },
    "symfony": {
        "nom": "Symfony", "langage": "PHP", "version": "7.x",
        "couleur": "white", "icone": "⚫",
        "signatures": ["bin/console"],
        "install": "composer create-project symfony/skeleton nom",
        "init_fn": "init_symfony",
        "fichiers_natifs": ["bin/console"],
        "notes": [
            "php bin/console make:entity pour les entités",
            "php bin/console make:controller pour les contrôleurs",
            "Doctrine ORM pour la base de données",
        ]
    },
    "spring": {
        "nom": "Spring Boot", "langage": "Java", "version": "3.x",
        "couleur": "green", "icone": "🍃",
        "signatures": ["pom.xml", "build.gradle"],
        "install": "spring init --dependencies=web,jpa,mysql,security nom",
        "init_fn": "init_spring",
        "fichiers_natifs": ["pom.xml", "src/main/java", "src/main/resources"],
        "notes": [
            "@SpringBootApplication sur la classe principale",
            "@RestController pour les API REST",
            "@Entity et @Repository pour JPA",
            "application.properties pour la config",
        ]
    },
    "express": {
        "nom": "Express.js", "langage": "JavaScript", "version": "4.x/5.x",
        "couleur": "yellow", "icone": "🟡",
        "signatures": [],
        "contenu_cles": ["require('express')", "express()", "app.listen"],
        "install": "npm init -y && npm install express dotenv cors helmet",
        "init_fn": "init_express",
        "fichiers_natifs": [],
        "notes": [
            "express.Router() pour les routes modulaires",
            "Prisma ou Sequelize pour la BDD",
            "JWT pour l'authentification",
        ]
    },
    "nestjs": {
        "nom": "NestJS", "langage": "TypeScript", "version": "10.x",
        "couleur": "red", "icone": "🔺",
        "signatures": ["nest-cli.json"],
        "install": "npm i -g @nestjs/cli && nest new nom",
        "init_fn": "init_nestjs",
        "fichiers_natifs": ["nest-cli.json", "src/app.module.ts", "src/main.ts"],
        "notes": [
            "nest g module/controller/service pour générer",
            "TypeORM ou Prisma pour la BDD",
            "DTOs avec class-validator",
        ]
    },
    "react": {
        "nom": "React", "langage": "JavaScript", "version": "18.x",
        "couleur": "cyan", "icone": "⚛",
        "signatures": [],
        "contenu_cles": ["from 'react'", "useState", "useEffect", "ReactDOM"],
        "install": "npm create vite@latest . -- --template react",
        "init_fn": "init_react",
        "fichiers_natifs": ["src/App.jsx", "src/main.jsx"],
        "notes": [
            "Hooks uniquement — pas de class components",
            "Vite comme bundler",
            "React Router v6 pour la navigation",
        ]
    },
    "nextjs": {
        "nom": "Next.js", "langage": "TypeScript", "version": "14.x/15.x",
        "couleur": "white", "icone": "▲",
        "signatures": ["next.config.js", "next.config.ts"],
        "install": "npx create-next-app@latest nom",
        "init_fn": "init_nextjs",
        "fichiers_natifs": ["next.config.js", "app/", "pages/"],
        "notes": [
            "App Router (app/) recommandé",
            "'use client' pour les composants interactifs",
            "Server Actions pour les formulaires",
        ]
    },
    "vue": {
        "nom": "Vue.js", "langage": "JavaScript", "version": "3.x",
        "couleur": "green", "icone": "💚",
        "signatures": [],
        "contenu_cles": ["from 'vue'", "createApp", "defineComponent", ".vue"],
        "install": "npm create vue@latest",
        "init_fn": "init_vue",
        "fichiers_natifs": ["src/App.vue"],
        "notes": [
            "Composition API avec script setup",
            "Pinia pour le state management",
            "Vue Router 4 pour la navigation",
        ]
    },
    "angular": {
        "nom": "Angular", "langage": "TypeScript", "version": "17.x/18.x",
        "couleur": "red", "icone": "🔴",
        "signatures": ["angular.json"],
        "install": "npm i -g @angular/cli && ng new nom",
        "init_fn": "init_angular",
        "fichiers_natifs": ["angular.json"],
        "notes": [
            "ng generate component/service pour générer",
            "Standalone components recommandés",
            "Signals pour la réactivité",
        ]
    },
    "react-native": {
        "nom": "React Native / Expo", "langage": "JavaScript", "version": "0.73+",
        "couleur": "cyan", "icone": "📱",
        "signatures": ["app.json", "expo.json"],
        "install": "npx create-expo-app@latest nom",
        "init_fn": "init_react_native",
        "fichiers_natifs": ["app.json", "App.js"],
        "notes": [
            "Expo SDK recommandé",
            "React Navigation pour la navigation",
            "StyleSheet.create pour les styles",
        ]
    },
    "flutter": {
        "nom": "Flutter", "langage": "Dart", "version": "3.x",
        "couleur": "cyan", "icone": "💙",
        "signatures": ["pubspec.yaml"],
        "install": "flutter create nom",
        "init_fn": "init_flutter",
        "fichiers_natifs": ["pubspec.yaml", "lib/main.dart"],
        "notes": [
            "StatelessWidget et StatefulWidget",
            "Provider ou Riverpod pour le state",
            "GoRouter pour la navigation",
        ]
    },
    "aucun": {
        "nom": "Langage libre", "langage": "Tous", "version": "",
        "couleur": "white", "icone": "📝",
        "signatures": [], "install": "", "init_fn": None,
        "fichiers_natifs": [], "notes": []
    }
}


# ============================================================
#  DETECTION — basée sur fichiers signatures uniquement
# ============================================================
def detecter_framework(path, fichiers):
    """
    Détection fiable basée sur des fichiers signatures uniques.
    Ne détecte rien si pas de preuve concrète.
    """
    noms = [n.lower().replace("\\", "/") for n in fichiers.keys()]

    for cle, fw in FRAMEWORKS.items():
        if cle == "aucun":
            continue
        for sig in fw.get("signatures", []):
            sig_lower = sig.lower()
            if any(n == sig_lower or n.endswith("/" + sig_lower) for n in noms):
                return cle

    return None  # Aucune signature trouvée → pas de détection


# ============================================================
#  CONFIRMATION
# ============================================================
def confirmer_framework(detecte):
    """Framework détecté — demande confirmation."""
    if not detecte:
        return None
    fw = FRAMEWORKS[detecte]
    console.print()
    console.print(
        f"[bold cyan][>>] Framework détecté :[/bold cyan] "
        f"{fw['icone']} [bold {fw['couleur']}]{fw['nom']} {fw['version']}[/bold {fw['couleur']}]"
    )
    if confirmer("C'est correct ?", defaut=True):
        ok(f"Mode [bold]{fw['nom']}[/bold] activé")
        _afficher_notes(detecte)
        return detecte
    return choisir_framework()


def choisir_framework():
    """Affiche la liste et demande le choix."""
    console.print("\n[bold cyan]Frameworks disponibles :[/bold cyan]\n")
    items = [(k, v) for k, v in FRAMEWORKS.items()]
    for i, (cle, fw) in enumerate(items, 1):
        lang = f"[dim]{fw['langage']}[/dim]"
        console.print(f"  [bold]{i:2}.[/bold] [{fw['couleur']}]{fw['icone']} {fw['nom']}[/{fw['couleur']}]  {lang}")

    console.print()
    choix = console.input("[cyan]Choisis un framework (numéro) : [/cyan]").strip()

    try:
        idx = int(choix) - 1
        if 0 <= idx < len(items):
            cle = items[idx][0]
            ok(f"Mode [bold]{FRAMEWORKS[cle]['nom']}[/bold] activé")
            _afficher_notes(cle)
            return cle
    except ValueError:
        pass

    warn("Choix invalide — mode langage libre.")
    return "aucun"


def _afficher_notes(cle):
    notes = FRAMEWORKS.get(cle, {}).get("notes", [])
    if not notes:
        return
    fw = FRAMEWORKS[cle]
    console.print(f"\n[dim]Bonnes pratiques {fw['nom']} v{fw.get('version','')} :[/dim]")
    for n in notes:
        console.print(f"  [dim]•[/dim] [dim]{n}[/dim]")
    console.print()


# ============================================================
#  INIT
# ============================================================
def init_framework(cle, path):
    fw = FRAMEWORKS.get(cle, {})
    fn = fw.get("init_fn")
    if not fn:
        warn("Pas d'initialisation pour ce framework.")
        return False
    fns = {
        "init_django":       _init_django,
        "init_fastapi":      _init_fastapi,
        "init_flask":        _init_flask,
        "init_laravel":      _init_laravel,
        "init_symfony":      _init_symfony,
        "init_spring":       _init_spring,
        "init_express":      _init_express,
        "init_nestjs":       _init_nestjs,
        "init_react":        _init_react,
        "init_nextjs":       _init_nextjs,
        "init_vue":          _init_vue,
        "init_angular":      _init_angular,
        "init_react_native": _init_react_native,
        "init_flutter":      _init_flutter,
    }
    return fns[fn](Path(path)) if fn in fns else False


def _run(cmd, cwd, label):
    info(f"{label}...")
    try:
        r = subprocess.run(
            cmd, cwd=str(cwd), shell=isinstance(cmd, str),
            capture_output=True, text=True, timeout=180
        )
        if r.returncode == 0:
            ok(label)
            return True
        err(f"{label} — {r.stderr.strip()[:200]}")
        return False
    except FileNotFoundError:
        err(f"Commande introuvable : {cmd[0] if isinstance(cmd, list) else cmd}")
        return False
    except subprocess.TimeoutExpired:
        err(f"Timeout — {label}")
        return False


def _verifier_outil(cmd, nom, hint):
    try:
        subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
        return True
    except FileNotFoundError:
        err(f"{nom} non trouvé. Installe : {hint}")
        return False


def _gitignore(path, type_):
    contenu = {
        "python": "*.pyc\n__pycache__/\n.env\nvenv/\n.venv/\ndb.sqlite3\nmedia/\nstaticfiles/\nrolax1212.log\n",
        "node":   "node_modules/\n.env\ndist/\nbuild/\n.next/\nrolax1212.log\n",
    }
    (path / ".gitignore").write_text(contenu.get(type_, ".env\nrolax1212.log\n"))
    ok(".gitignore créé")


def _init_django(path):
    nom  = console.input("[cyan]Nom du projet Django [le_restaurant] : [/cyan]").strip() or "le_restaurant"
    apps = console.input("[cyan]Apps à créer (virgule) [restaurant] : [/cyan]").strip() or "restaurant"
    apps = [a.strip() for a in apps.split(",") if a.strip()]

    try:
        subprocess.run(["python", "-m", "django", "--version"], capture_output=True, check=True, timeout=5)
    except Exception:
        _run("pip install django mysqlclient pillow python-decouple", path, "pip install django")

    _run(["django-admin", "startproject", nom, "."], path, f"startproject {nom}")
    for app in apps:
        _run(["python", "manage.py", "startapp", app], path, f"startapp {app}")

    for d in ["templates", "static/css", "static/js", "static/img", "media"]:
        (path / d).mkdir(parents=True, exist_ok=True)
        ok(f"{d}/")

    (path / "requirements.txt").write_text("Django>=4.2\nmysqlclient>=2.2\nPillow>=10.0\npython-decouple>=3.8\n")
    _gitignore(path, "python")
    ok(f"\nProjet Django '{nom}' prêt !")
    console.print("  [cyan]1.[/cyan] Configurer settings.py")
    console.print("  [cyan]2.[/cyan] python manage.py migrate")
    console.print("  [cyan]3.[/cyan] python manage.py createsuperuser")
    return True


def _init_fastapi(path):
    _run("pip install fastapi uvicorn sqlalchemy pydantic python-dotenv", path, "pip install fastapi")
    for d in ["app/routers", "app/models", "app/schemas"]:
        (path / d).mkdir(parents=True, exist_ok=True)
    (path / "app/__init__.py").write_text("")
    (path / "app/main.py").write_text('from fastapi import FastAPI\napp = FastAPI()\n\n@app.get("/")\ndef root():\n    return {"ok": True}\n')
    (path / "requirements.txt").write_text("fastapi>=0.110\nuvicorn>=0.27\nsqlalchemy>=2.0\npydantic>=2.0\n")
    _gitignore(path, "python")
    ok("FastAPI prêt ! Lance : uvicorn app.main:app --reload")
    return True


def _init_flask(path):
    _run("pip install flask flask-sqlalchemy flask-login flask-migrate python-dotenv", path, "pip install flask")
    for d in ["app/templates", "app/static/css", "app/models", "app/routes"]:
        (path / d).mkdir(parents=True, exist_ok=True)
    (path / "app/__init__.py").write_text('from flask import Flask\nfrom flask_sqlalchemy import SQLAlchemy\ndb = SQLAlchemy()\n\ndef create_app():\n    app = Flask(__name__)\n    db.init_app(app)\n    return app\n')
    (path / "run.py").write_text('from app import create_app\napp = create_app()\nif __name__ == "__main__":\n    app.run(debug=True)\n')
    _gitignore(path, "python")
    ok("Flask prêt ! Lance : python run.py")
    return True


def _init_laravel(path):
    if not _verifier_outil("composer", "Composer", "https://getcomposer.org"):
        return False
    nom = console.input("[cyan]Nom du projet Laravel : [/cyan]").strip() or "mon-laravel"
    _run(["composer", "create-project", "laravel/laravel", str(path / nom)], path, f"laravel/laravel {nom}")
    ok(f"Laravel '{nom}' prêt ! Lance : cd {nom} && php artisan serve")
    return True


def _init_symfony(path):
    if not _verifier_outil("composer", "Composer", "https://getcomposer.org"):
        return False
    nom = console.input("[cyan]Nom du projet Symfony : [/cyan]").strip() or "mon-symfony"
    _run(["composer", "create-project", "symfony/skeleton", str(path / nom)], path, f"symfony/skeleton {nom}")
    ok(f"Symfony '{nom}' prêt !")
    return True


def _init_spring(path):
    warn("Génère ton projet sur : https://start.spring.io")
    console.print("  Extrais-le ici puis : mvn spring-boot:run")
    return True


def _init_express(path):
    _run(["npm", "init", "-y"], path, "npm init")
    _run(["npm", "install", "express", "dotenv", "cors", "helmet"], path, "npm install express")
    for d in ["src/routes", "src/controllers", "src/models"]:
        (path / d).mkdir(parents=True, exist_ok=True)
    (path / "src/app.js").write_text("const express = require('express');\nconst app = express();\napp.use(express.json());\napp.get('/', (req,res) => res.json({ok:true}));\nmodule.exports = app;\n")
    (path / "src/server.js").write_text("const app = require('./app');\napp.listen(3000, () => console.log('Server on port 3000'));\n")
    _gitignore(path, "node")
    ok("Express prêt ! Lance : node src/server.js")
    return True


def _init_nestjs(path):
    nom = console.input("[cyan]Nom du projet NestJS : [/cyan]").strip() or "mon-nest"
    if not _verifier_outil("nest", "NestJS CLI", "npm i -g @nestjs/cli"):
        _run(["npm", "install", "-g", "@nestjs/cli"], path, "install @nestjs/cli")
    _run(["nest", "new", nom, "--skip-git"], path, f"nest new {nom}")
    ok(f"NestJS '{nom}' prêt !")
    return True


def _init_react(path):
    _run(["npm", "create", "vite@latest", ".", "--", "--template", "react"], path, "create vite react")
    _run(["npm", "install"], path, "npm install")
    _gitignore(path, "node")
    ok("React (Vite) prêt ! Lance : npm run dev")
    return True


def _init_nextjs(path):
    nom = console.input("[cyan]Nom du projet Next.js : [/cyan]").strip() or "mon-next"
    _run(["npx", "create-next-app@latest", nom], path, f"create-next-app {nom}")
    ok(f"Next.js '{nom}' prêt !")
    return True


def _init_vue(path):
    _run(["npm", "create", "vue@latest", "."], path, "create vue")
    _run(["npm", "install"], path, "npm install")
    ok("Vue.js prêt ! Lance : npm run dev")
    return True


def _init_angular(path):
    nom = console.input("[cyan]Nom du projet Angular : [/cyan]").strip() or "mon-angular"
    if not _verifier_outil("ng", "Angular CLI", "npm i -g @angular/cli"):
        _run(["npm", "install", "-g", "@angular/cli"], path, "install @angular/cli")
    _run(["ng", "new", nom], path, f"ng new {nom}")
    ok(f"Angular '{nom}' prêt !")
    return True


def _init_react_native(path):
    nom = console.input("[cyan]Nom de l'app : [/cyan]").strip() or "MonApp"
    _run(["npx", "create-expo-app@latest", nom], path, f"create-expo-app {nom}")
    ok(f"React Native '{nom}' prêt ! Lance : cd {nom} && npx expo start")
    return True


def _init_flutter(path):
    nom = console.input("[cyan]Nom de l'app Flutter : [/cyan]").strip() or "mon_app"
    if not _verifier_outil("flutter", "Flutter", "https://flutter.dev"):
        return False
    _run(["flutter", "create", nom], path, f"flutter create {nom}")
    ok(f"Flutter '{nom}' prêt ! Lance : cd {nom} && flutter run")
    return True


# ============================================================
#  PROMPT SYSTEME ADAPTE AU FRAMEWORK
# ============================================================
def prompt_framework(cle):
    fw = FRAMEWORKS.get(cle)
    if not fw or cle == "aucun":
        return ""

    notes   = fw.get("notes", [])
    natifs  = fw.get("fichiers_natifs", [])
    prompt  = f"\n\nFRAMEWORK : {fw['nom']} {fw['version']} ({fw['langage']})\n"

    if notes:
        prompt += "\nRÈGLES OBLIGATOIRES :\n" + "\n".join(f"- {n}" for n in notes)

    if natifs:
        prompt += f"\n\nFICHIERS CRÉÉS PAR LE FRAMEWORK (ne pas recréer manuellement) :\n"
        prompt += "\n".join(f"- {f}" for f in natifs)
        prompt += "\nModifie-les seulement si la tâche le demande explicitement.\n"

    return prompt
