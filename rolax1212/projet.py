# ============================================================
#  projet.py — Lecture et gestion du projet
#  rolax1212 v2.0.1 by Roland
# ============================================================

import re
import os
import subprocess
import sys
from pathlib import Path
from .ui import console, ok, info, warn, err, separateur

EXTENSIONS_CODE = {
    ".py": "python", ".php": "php", ".java": "java",
    ".js": "javascript", ".ts": "typescript",
    ".html": "html", ".css": "css", ".sql": "sql",
    ".sh": "bash", ".md": "markdown", ".json": "json",
    ".xml": "xml", ".c": "c", ".cpp": "cpp", ".h": "c",
    ".txt": "text", ".env": "text", ".yaml": "yaml",
    ".yml": "yaml", ".toml": "toml", ".ini": "ini",
    ".dart": "dart",
}

IGNORER = {
    "node_modules", ".git", "__pycache__", "venv", ".venv",
    "dist", "build", ".idea", ".vscode", "vendor", "target",
    ".next", ".nuxt", "coverage", ".pytest_cache", "rolax1212.egg-info",
    "v2 files", "v2files"
}

MAX_FICHIER = 8000
MAX_PROJET  = 40000


def lire_projet(path_str):
    path = Path(path_str).resolve()
    if not path.exists():
        err(f"Chemin introuvable : {path}")
        return None, {}

    fichiers    = {}
    total_chars = 0
    tronque     = False

    tous = sorted(path.rglob("*"), key=lambda p: (
        0 if p.suffix in [".md", ".json", ".env", ".txt"] else 1
    ))

    for f in tous:
        if not f.is_file():
            continue
        if any(ign in f.parts for ign in IGNORER):
            continue
        if f.suffix not in EXTENSIONS_CODE:
            continue
        try:
            contenu = f.read_text(encoding="utf-8", errors="ignore")
            if not contenu.strip():
                continue
            if len(contenu) > MAX_FICHIER:
                contenu = contenu[:MAX_FICHIER] + f"\n... [TRONQUÉ]"
            rel = str(f.relative_to(path))
            fichiers[rel] = contenu
            total_chars  += len(contenu)
            if total_chars > MAX_PROJET:
                tronque = True
                break
        except Exception:
            continue

    if tronque:
        warn("Projet volumineux — contexte partiel chargé.")

    return path, fichiers


def construire_contexte(fichiers):
    if not fichiers:
        return "Projet vide."
    ctx = "STRUCTURE :\n" + "\n".join(f"  - {f}" for f in fichiers) + "\n"
    for chemin, contenu in fichiers.items():
        lang = EXTENSIONS_CODE.get(Path(chemin).suffix, "")
        ctx += f"\n{'='*48}\nFICHIER : {chemin}\n{'='*48}\n```{lang}\n{contenu}\n```\n"
    return ctx


def afficher_structure(path, fichiers):
    from rich.table import Table
    t = Table(title=f"Projet : {path}", style="cyan")
    t.add_column("Fichier",  style="white")
    t.add_column("Langage",  style="yellow")
    t.add_column("Lignes",   justify="right", style="green")
    for chemin, contenu in fichiers.items():
        lang = EXTENSIONS_CODE.get(Path(chemin).suffix, "?")
        t.add_row(chemin, lang, str(len(contenu.splitlines())))
    console.print(t)


def extraire_blocs(reponse):
    pattern = r"```(\w*)\n(.*?)```"
    blocs   = re.findall(pattern, reponse, re.DOTALL)
    parties = re.split(r"```\w*\n.*?```", reponse, flags=re.DOTALL)

    resultats = []
    for i, (lang, contenu) in enumerate(blocs):
        if not contenu.strip():
            continue
        nom            = None
        contexte_avant = parties[i] if i < len(parties) else ""
        dernieres      = "\n".join(contexte_avant.strip().splitlines()[-6:])

        patterns_nom = [
            r"FICHIER\s*:\s*([^\s\n`]+\.\w+)",
            r"fichier\s*`([^`]+\.\w+)`",
            r"`([a-zA-Z0-9_\-/]+\.\w+)`",
            r"\*\*([a-zA-Z0-9_\-/]+\.\w+)\*\*",
            r"###?\s+([a-zA-Z0-9_\-/]+\.\w+)",
            r"(?:créer?|crée?|génér|fichier)\s+([a-zA-Z0-9_\-/]+\.\w+)",
            r"([a-zA-Z0-9_\-/]+\.(?:php|py|js|java|html|css|sql|ts|sh|md|dart))\s*:",
        ]
        for pat in patterns_nom:
            m = re.search(pat, dernieres, re.IGNORECASE)
            if m:
                nom = m.group(1).strip()
                break
        if not nom:
            for pat in patterns_nom:
                m = re.search(pat, contexte_avant, re.IGNORECASE)
                if m:
                    nom = m.group(1).strip()
                    break

        resultats.append({"lang": lang or "text", "code": contenu.strip(), "nom": nom})
    return resultats


def sauvegarder(chemin, contenu):
    p = Path(chemin)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(contenu, encoding="utf-8")
    ok(f"Fichier créé : {chemin}")


def executer(chemin, cwd=None):
    p   = Path(chemin)
    cwd = cwd or p.parent
    cmds = {
        ".py": [sys.executable, str(p)],
        ".sh": ["bash", str(p)],
        ".php": ["php", str(p)],
        ".js": ["node", str(p)],
    }
    cmd = cmds.get(p.suffix)
    if not cmd:
        return None, "", f"Extension {p.suffix} non exécutable."
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(cwd))
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def lire_task(path):
    for nom in ["Task.md", "task.md", "TASK.md", "tasks.md", "TODO.md"]:
        p = Path(path) / nom
        if p.exists():
            return p, p.read_text(encoding="utf-8")
    return None, None


def extraire_taches(contenu):
    taches = []
    for ligne in contenu.splitlines():
        l = ligne.strip()
        if l.startswith("- [ ]"):
            t = l[5:].strip()
            if t:
                taches.append(t)
    return taches


def marquer_tache_faite(path_task, tache):
    try:
        contenu = Path(path_task).read_text(encoding="utf-8")
        Path(path_task).write_text(
            contenu.replace(f"- [ ] {tache}", f"- [x] {tache}", 1),
            encoding="utf-8"
        )
    except Exception:
        pass
