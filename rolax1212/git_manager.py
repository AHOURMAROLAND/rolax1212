# ============================================================
#  git_manager.py — Gestion Git automatique
#  rolax1212 v2.0.1 by Roland
# ============================================================

import subprocess
from pathlib import Path
from .ui  import console, ok, info, warn, err, confirmer
from .llm import demander


def git_disponible():
    try:
        subprocess.run(["git", "--version"], capture_output=True, timeout=5)
        return True
    except FileNotFoundError:
        return False


def est_repo_git(path):
    return (Path(path) / ".git").exists()


def _run(cmd, cwd):
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def init_git(path):
    if not git_disponible():
        err("Git non installé : https://git-scm.com")
        return False
    if est_repo_git(path):
        info("Repo Git déjà initialisé.")
        return True
    code, _, e = _run(["git", "init"], path)
    if code == 0:
        ok("Repo Git initialisé")
        gitignore = Path(path) / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*.pyc\n__pycache__/\n.env\nvenv/\nnode_modules/\ndist/\nrolax1212.log\n")
            ok(".gitignore créé")
        return True
    err(f"git init échoué : {e}")
    return False


def statut(path):
    code, out, _ = _run(["git", "status", "--short"], path)
    if code != 0 or not out:
        return []
    return [{"statut": l[:2].strip(), "fichier": l[3:].strip()} for l in out.splitlines() if l.strip()]


def afficher_statut(path):
    if not est_repo_git(path):
        warn("Pas de repo Git. Tape 'init git' pour initialiser.")
        return
    fichiers = statut(path)
    if not fichiers:
        ok("Rien à committer — working tree clean")
        return
    console.print(f"\n[bold cyan]Fichiers modifiés ({len(fichiers)}) :[/bold cyan]")
    for f in fichiers:
        c = "green" if f["statut"] in ["A", "?"] else "yellow" if f["statut"] == "M" else "red"
        console.print(f"  [{c}]{f['statut']}[/{c}]  {f['fichier']}")
    console.print()


def commit_auto(path, modele, historique):
    if not git_disponible():
        err("Git non installé.")
        return False
    if not est_repo_git(path):
        if confirmer("Pas de repo Git. Initialiser ?"):
            init_git(path)
        else:
            return False

    modifies = statut(path)
    if not modifies:
        ok("Rien à committer.")
        return True

    afficher_statut(path)

    # Génère le message via LLM
    info("Génération du message de commit...")
    noms = ", ".join(f["fichier"] for f in modifies[:10])
    prompt = (
        f"Génère un message de commit Git court (max 72 chars) en français.\n"
        f"Fichiers modifiés : {noms}\n"
        f"Format : type(scope): description\n"
        f"Types : feat, fix, refactor, style, docs, chore\n"
        f"Réponds UNIQUEMENT avec le message, rien d'autre."
    )
    rep = demander(historique + [{"role": "user", "content": prompt}], modele, stream=False, timeout=60)
    message = (rep or f"chore: mise à jour {len(modifies)} fichier(s)").strip().strip('"').strip("'").splitlines()[0]

    console.print(f"\n[bold yellow]Message :[/bold yellow] {message}")
    if not confirmer("Effectuer ce commit ?", defaut=True):
        warn("Commit annulé.")
        return False

    _run(["git", "add", "."], path)
    code, _, e = _run(["git", "commit", "-m", message], path)
    if code == 0:
        ok(f"Commit : {message}")
        return True
    err(f"Commit échoué : {e}")
    return False


def commit_message_libre(path, message):
    if not est_repo_git(path):
        err("Pas de repo Git.")
        return False
    _run(["git", "add", "."], path)
    code, _, e = _run(["git", "commit", "-m", message], path)
    if code == 0:
        ok(f"Commit : {message}")
        return True
    err(f"Erreur : {e}")
    return False


def historique_git(path, nb=10):
    code, out, _ = _run(["git", "log", f"--max-count={nb}", "--oneline", "--decorate"], path)
    if code != 0 or not out:
        warn("Aucun commit trouvé.")
        return
    console.print(f"\n[bold cyan]Derniers {nb} commits :[/bold cyan]")
    for l in out.splitlines():
        console.print(f"  [dim]{l}[/dim]")
    console.print()


def push(path):
    code, _, e = _run(["git", "push"], path)
    if code == 0:
        ok("Push effectué")
    else:
        warn(f"Push échoué : {e[:200]}")
        warn("Configure : git remote add origin [url]")
