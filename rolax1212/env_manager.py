# ============================================================
#  env_manager.py — Gestion variables d'environnement
#  rolax1212 v4.1.0 by Roland
# ============================================================

import re
from pathlib import Path
from .ui import console, ok, info, warn, err, separateur, confirmer, titre

# ── Variables requises par framework ────────────────────────
ENV_PAR_FRAMEWORK = {
    "django": [
        {"cle": "SECRET_KEY",      "desc": "Clé secrète Django",          "defaut": "",        "secret": True},
        {"cle": "DEBUG",           "desc": "Mode debug (True/False)",      "defaut": "True",    "secret": False},
        {"cle": "ALLOWED_HOSTS",   "desc": "Hosts autorisés",              "defaut": "localhost,127.0.0.1", "secret": False},
        {"cle": "DB_ENGINE",       "desc": "Moteur BDD (django.db.backends.mysql / sqlite3...)", "defaut": "django.db.backends.sqlite3", "secret": False},
        {"cle": "DB_NAME",         "desc": "Nom de la base de données",    "defaut": "db.sqlite3", "secret": False},
        {"cle": "DB_USER",         "desc": "Utilisateur BDD",              "defaut": "root",    "secret": False},
        {"cle": "DB_PASSWORD",     "desc": "Mot de passe BDD",             "defaut": "",        "secret": True},
        {"cle": "DB_HOST",         "desc": "Hôte BDD",                    "defaut": "localhost","secret": False},
        {"cle": "DB_PORT",         "desc": "Port BDD",                    "defaut": "3306",    "secret": False},
    ],
    "fastapi": [
        {"cle": "DATABASE_URL",    "desc": "URL de connexion BDD",        "defaut": "sqlite:///./app.db", "secret": False},
        {"cle": "SECRET_KEY",      "desc": "Clé secrète JWT",             "defaut": "",        "secret": True},
        {"cle": "DEBUG",           "desc": "Mode debug (True/False)",     "defaut": "True",    "secret": False},
        {"cle": "HOST",            "desc": "Hôte serveur",               "defaut": "0.0.0.0", "secret": False},
        {"cle": "PORT",            "desc": "Port serveur",               "defaut": "8000",    "secret": False},
    ],
    "flask": [
        {"cle": "SECRET_KEY",      "desc": "Clé secrète Flask",           "defaut": "",        "secret": True},
        {"cle": "DATABASE_URL",    "desc": "URL de connexion BDD",        "defaut": "sqlite:///app.db", "secret": False},
        {"cle": "DEBUG",           "desc": "Mode debug (True/False)",     "defaut": "True",    "secret": False},
        {"cle": "FLASK_ENV",       "desc": "Environnement (development/production)", "defaut": "development", "secret": False},
    ],
    "laravel": [
        {"cle": "APP_NAME",        "desc": "Nom de l'application",        "defaut": "Laravel", "secret": False},
        {"cle": "APP_ENV",         "desc": "Environnement (local/production)", "defaut": "local", "secret": False},
        {"cle": "APP_KEY",         "desc": "Clé applicative (php artisan key:generate)", "defaut": "", "secret": True},
        {"cle": "APP_DEBUG",       "desc": "Mode debug (true/false)",     "defaut": "true",    "secret": False},
        {"cle": "APP_URL",         "desc": "URL de l'application",        "defaut": "http://localhost", "secret": False},
        {"cle": "DB_CONNECTION",   "desc": "Driver BDD (mysql/sqlite...)", "defaut": "mysql",  "secret": False},
        {"cle": "DB_HOST",         "desc": "Hôte BDD",                   "defaut": "127.0.0.1","secret": False},
        {"cle": "DB_PORT",         "desc": "Port BDD",                   "defaut": "3306",    "secret": False},
        {"cle": "DB_DATABASE",     "desc": "Nom de la base de données",  "defaut": "laravel", "secret": False},
        {"cle": "DB_USERNAME",     "desc": "Utilisateur BDD",            "defaut": "root",    "secret": False},
        {"cle": "DB_PASSWORD",     "desc": "Mot de passe BDD",           "defaut": "",        "secret": True},
    ],
    "symfony": [
        {"cle": "APP_ENV",         "desc": "Environnement (dev/prod)",    "defaut": "dev",     "secret": False},
        {"cle": "APP_SECRET",      "desc": "Secret applicatif",           "defaut": "",        "secret": True},
        {"cle": "DATABASE_URL",    "desc": "URL Doctrine (mysql://user:pass@host/db)", "defaut": "mysql://root:@127.0.0.1:3306/symfony", "secret": False},
    ],
    "express": [
        {"cle": "PORT",            "desc": "Port serveur",               "defaut": "3000",    "secret": False},
        {"cle": "NODE_ENV",        "desc": "Environnement (development/production)", "defaut": "development", "secret": False},
        {"cle": "DATABASE_URL",    "desc": "URL de connexion BDD",        "defaut": "",        "secret": False},
        {"cle": "JWT_SECRET",      "desc": "Clé secrète JWT",            "defaut": "",        "secret": True},
    ],
    "nestjs": [
        {"cle": "PORT",            "desc": "Port serveur",               "defaut": "3000",    "secret": False},
        {"cle": "NODE_ENV",        "desc": "Environnement",              "defaut": "development", "secret": False},
        {"cle": "DATABASE_URL",    "desc": "URL de connexion BDD",       "defaut": "",        "secret": False},
        {"cle": "JWT_SECRET",      "desc": "Clé secrète JWT",           "defaut": "",        "secret": True},
        {"cle": "JWT_EXPIRES_IN",  "desc": "Expiration token JWT",      "defaut": "7d",      "secret": False},
    ],
    "nextjs": [
        {"cle": "NEXTAUTH_SECRET", "desc": "Secret NextAuth",           "defaut": "",        "secret": True},
        {"cle": "NEXTAUTH_URL",    "desc": "URL de l'app",              "defaut": "http://localhost:3000", "secret": False},
        {"cle": "DATABASE_URL",    "desc": "URL de connexion BDD",      "defaut": "",        "secret": False},
    ],
    "react": [
        {"cle": "VITE_API_URL",    "desc": "URL de l'API backend",      "defaut": "http://localhost:3000", "secret": False},
    ],
    "vue": [
        {"cle": "VITE_API_URL",    "desc": "URL de l'API backend",      "defaut": "http://localhost:3000", "secret": False},
    ],
    "spring": [
        {"cle": "DB_URL",          "desc": "URL JDBC (jdbc:mysql://localhost:3306/db)", "defaut": "", "secret": False},
        {"cle": "DB_USERNAME",     "desc": "Utilisateur BDD",           "defaut": "root",    "secret": False},
        {"cle": "DB_PASSWORD",     "desc": "Mot de passe BDD",          "defaut": "",        "secret": True},
        {"cle": "JWT_SECRET",      "desc": "Clé secrète JWT",          "defaut": "",        "secret": True},
    ],
}

# Variables génériques si framework inconnu ou "aucun"
ENV_GENERIQUE = [
    {"cle": "APP_ENV",    "desc": "Environnement (development/production)", "defaut": "development", "secret": False},
    {"cle": "SECRET_KEY", "desc": "Clé secrète applicative",               "defaut": "",            "secret": True},
    {"cle": "DATABASE_URL","desc": "URL de connexion BDD (optionnel)",      "defaut": "",            "secret": False},
]


# ============================================================
#  LECTURE / ECRITURE .env
# ============================================================
def _lire_env(path_projet) -> dict:
    """Lit un fichier .env et retourne un dict {CLE: valeur}."""
    env_path = Path(path_projet) / ".env"
    if not env_path.exists():
        return {}
    vars_env = {}
    for ligne in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        if "=" in ligne:
            cle, _, val = ligne.partition("=")
            vars_env[cle.strip()] = val.strip()
    return vars_env


def _lire_env_example(path_projet) -> dict:
    """Lit .env.example ou .env.example.dist comme template."""
    for nom in [".env.example", ".env.example.dist", ".env.sample", ".env.template"]:
        p = Path(path_projet) / nom
        if p.exists():
            vars_env = {}
            for ligne in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                ligne = ligne.strip()
                if not ligne or ligne.startswith("#"):
                    continue
                if "=" in ligne:
                    cle, _, val = ligne.partition("=")
                    vars_env[cle.strip()] = val.strip()
            return vars_env, nom
    return {}, None


def _ecrire_env(path_projet, vars_env: dict, vars_existantes: dict):
    """Écrit / met à jour le .env en préservant les valeurs existantes."""
    env_path = Path(path_projet) / ".env"

    # Charge le contenu existant ligne par ligne
    lignes_existantes = []
    if env_path.exists():
        lignes_existantes = env_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Met à jour ou ajoute les nouvelles variables
    cles_traitees = set()
    nouvelles_lignes = []

    for ligne in lignes_existantes:
        stripped = ligne.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            cle = stripped.split("=", 1)[0].strip()
            if cle in vars_env:
                nouvelles_lignes.append(f"{cle}={vars_env[cle]}")
                cles_traitees.add(cle)
                continue
        nouvelles_lignes.append(ligne)

    # Ajoute les variables non encore présentes
    nouvelles = [k for k in vars_env if k not in cles_traitees]
    if nouvelles:
        nouvelles_lignes.append("")
        nouvelles_lignes.append("# Ajouté par rolax1212")
        for cle in nouvelles:
            nouvelles_lignes.append(f"{cle}={vars_env[cle]}")

    env_path.write_text("\n".join(nouvelles_lignes) + "\n", encoding="utf-8")
    ok(f".env mis à jour : {env_path}")


# ============================================================
#  INTERFACE PRINCIPALE
# ============================================================
def configurer_env(path_projet, framework=None, force=False):
    """
    Vérifie et configure les variables d'environnement du projet.
    - force=True : relance même si .env complet
    """
    path_projet = Path(path_projet)
    separateur()
    titre("Configuration des variables d'environnement")

    # Détermine les variables attendues
    vars_attendues = _get_vars_attendues(path_projet, framework)

    # Lit l'existant
    vars_actuelles = _lire_env(path_projet)
    vars_example, nom_example = _lire_env_example(path_projet)

    if nom_example:
        info(f"Template détecté : {nom_example}")
        # Fusionne les variables du template avec les attendues
        for cle, val in vars_example.items():
            if not any(v["cle"] == cle for v in vars_attendues):
                vars_attendues.append({
                    "cle": cle, "desc": "Variable du projet", 
                    "defaut": val, "secret": "KEY" in cle or "SECRET" in cle or "PASSWORD" in cle or "PASS" in cle
                })

    # Trouve les variables manquantes ou vides
    manquantes = []
    for var in vars_attendues:
        val_actuelle = vars_actuelles.get(var["cle"], "")
        if not val_actuelle or force:
            manquantes.append({**var, "actuelle": val_actuelle})

    if not manquantes and not force:
        ok(".env complet — toutes les variables sont configurées.")
        separateur()
        return vars_actuelles

    # Affiche le statut actuel
    if vars_actuelles:
        console.print(f"\n[dim].env existant — {len(vars_actuelles)} variable(s) trouvée(s)[/dim]")
        _afficher_statut_env(vars_attendues, vars_actuelles)
    else:
        warn(".env introuvable — création en cours...")

    if not manquantes:
        ok("Toutes les variables sont déjà définies.")
        separateur()
        return vars_actuelles

    console.print(f"\n[yellow]{len(manquantes)} variable(s) manquante(s) à configurer :[/yellow]\n")

    if not confirmer("Configurer les variables maintenant ?", defaut=True):
        warn("Configuration ignorée. Tu peux relancer avec la commande 'env'.")
        separateur()
        return vars_actuelles

    # Saisie interactive
    nouvelles_valeurs = {}
    for var in manquantes:
        cle     = var["cle"]
        desc    = var["desc"]
        defaut  = var["actuelle"] or var["defaut"]
        secret  = var["secret"]

        console.print(f"\n  [cyan]{cle}[/cyan]  [dim]{desc}[/dim]")

        if defaut:
            if secret:
                affichage_defaut = defaut[:4] + "..." if len(defaut) > 4 else "***"
            else:
                affichage_defaut = defaut
            console.print(f"  [dim]Défaut : {affichage_defaut}[/dim]")

        if secret:
            # Saisie masquée pour les secrets
            valeur = console.input(f"  [bold]{cle}[/bold] (secret) : ").strip()
        else:
            valeur = console.input(f"  [bold]{cle}[/bold] : ").strip()

        # Utilise le défaut si vide
        if not valeur and defaut:
            valeur = defaut
            console.print(f"  [dim]→ Valeur par défaut utilisée : {defaut if not secret else '***'}[/dim]")

        if valeur:
            nouvelles_valeurs[cle] = valeur

    if nouvelles_valeurs:
        _ecrire_env(path_projet, nouvelles_valeurs, vars_actuelles)
        console.print(f"\n[bold green]{len(nouvelles_valeurs)} variable(s) configurée(s) avec succès ![/bold green]")
    else:
        warn("Aucune valeur saisie.")

    separateur()
    return {**vars_actuelles, **nouvelles_valeurs}


def verifier_env_silencieux(path_projet, framework=None):
    """
    Vérification silencieuse au démarrage.
    Retourne True si tout est OK, False si des variables manquent.
    N'affiche un avertissement que si des variables critiques manquent.
    """
    vars_attendues = _get_vars_attendues(Path(path_projet), framework)
    if not vars_attendues:
        return True

    vars_actuelles = _lire_env(path_projet)
    manquantes_critiques = []

    for var in vars_attendues:
        val = vars_actuelles.get(var["cle"], "")
        # Variables critiques : sans défaut et non secrets basiques
        if not val and not var["defaut"] and var["cle"] not in ["SECRET_KEY", "APP_KEY", "APP_SECRET"]:
            manquantes_critiques.append(var["cle"])

    if manquantes_critiques:
        warn(f".env incomplet — variables manquantes : {', '.join(manquantes_critiques[:4])}")
        warn("Lance 'env' pour configurer.")
        return False
    return True


# ============================================================
#  HELPERS
# ============================================================
def _get_vars_attendues(path_projet, framework):
    """Retourne les variables attendues selon le framework."""
    # Vérifie si un .env.example existe → priorité
    _, nom_example = _lire_env_example(path_projet)
    if nom_example:
        return []  # sera peuplé depuis le template dans configurer_env

    if framework and framework in ENV_PAR_FRAMEWORK:
        return list(ENV_PAR_FRAMEWORK[framework])
    elif framework in [None, "aucun"]:
        # Détecte depuis les fichiers du projet
        fw_detecte = _detecter_framework_depuis_fichiers(path_projet)
        if fw_detecte and fw_detecte in ENV_PAR_FRAMEWORK:
            return list(ENV_PAR_FRAMEWORK[fw_detecte])
    return list(ENV_GENERIQUE)


def _detecter_framework_depuis_fichiers(path_projet):
    """Détection rapide par fichiers signatures pour env_manager."""
    signatures = {
        "manage.py":       "django",
        "artisan":         "laravel",
        "bin/console":     "symfony",
        "nest-cli.json":   "nestjs",
        "next.config.js":  "nextjs",
        "next.config.ts":  "nextjs",
        "angular.json":    "angular",
        "pubspec.yaml":    "flutter",
    }
    for fichier, fw in signatures.items():
        if (path_projet / fichier).exists():
            return fw
    # Détection par contenu package.json
    pkg = path_projet / "package.json"
    if pkg.exists():
        try:
            contenu = pkg.read_text(encoding="utf-8")
            if '"express"' in contenu:  return "express"
            if '"next"'    in contenu:  return "nextjs"
            if '"vue"'     in contenu:  return "vue"
            if '"react"'   in contenu:  return "react"
        except Exception:
            pass
    # requirements.txt
    req = path_projet / "requirements.txt"
    if req.exists():
        try:
            contenu = req.read_text(encoding="utf-8").lower()
            if "django"  in contenu: return "django"
            if "fastapi" in contenu: return "fastapi"
            if "flask"   in contenu: return "flask"
        except Exception:
            pass
    return None


def _afficher_statut_env(vars_attendues, vars_actuelles):
    """Affiche un tableau de statut des variables."""
    from rich.table import Table
    t = Table(style="dim", show_header=True, header_style="bold cyan")
    t.add_column("Variable",     style="white",  min_width=20)
    t.add_column("Statut",       style="white",  min_width=10)
    t.add_column("Valeur",       style="dim",    min_width=20)

    for var in vars_attendues:
        cle = var["cle"]
        val = vars_actuelles.get(cle, "")
        if val:
            statut  = "[green]✓ définie[/green]"
            affiche = ("***" if var["secret"] else (val[:30] + "..." if len(val) > 30 else val))
        else:
            statut  = "[red]✗ manquante[/red]"
            affiche = f"[dim]défaut: {var['defaut'] or 'aucun'}[/dim]"
        t.add_row(cle, statut, affiche)

    console.print(t)
