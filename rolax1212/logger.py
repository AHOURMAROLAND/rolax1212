# ============================================================
#  logger.py — Log de continuité
#  rolax1212 v2.0.1 by Roland
# ============================================================

import json
from datetime import datetime
from pathlib  import Path
from .ui import console, ok, info, warn, confirmer, separateur

LOG_FILE = "rolax1212.log"


class Logger:
    def __init__(self, path_projet):
        self.path    = Path(path_projet) / LOG_FILE
        self.entrees = []
        self._charger()

    def _charger(self):
        if self.path.exists():
            try:
                self.entrees = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self.entrees = []

    def _sauvegarder(self):
        self.path.write_text(json.dumps(self.entrees, ensure_ascii=False, indent=2), encoding="utf-8")

    def log(self, type_, message, details=None):
        entree = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "type": type_, "message": message}
        if details:
            entree["details"] = details
        self.entrees.append(entree)
        self._sauvegarder()

    def tache_debut(self, numero, total, tache):
        self.log("TACHE_DEBUT", f"Tâche {numero}/{total} — EN COURS", {"tache": tache, "numero": numero, "total": total})

    def tache_fin(self, numero, total, tache):
        self.log("TACHE_FIN", f"Tâche {numero}/{total} — DONE", {"tache": tache})

    def session_fin(self):
        self.log("SESSION_FIN", "Session terminée proprement")

    def derniere_tache_incomplete(self):
        debut = None
        fins  = set()
        for e in self.entrees:
            if e["type"] == "SESSION_FIN":
                debut, fins = None, set()
            elif e["type"] == "TACHE_DEBUT":
                debut = e
            elif e["type"] == "TACHE_FIN":
                if debut:
                    fins.add(debut["details"].get("numero"))
                    debut = None
        if debut and debut["details"].get("numero") not in fins:
            return debut
        return None

    def taches_restantes(self, toutes):
        terminees = {e["details"]["tache"] for e in self.entrees if e["type"] == "TACHE_FIN" and "details" in e}
        return [t for t in toutes if t not in terminees]

    def afficher_resume(self):
        if not self.entrees:
            return
        nb_t = sum(1 for e in self.entrees if e["type"] == "TACHE_FIN")
        if nb_t:
            console.print(f"[dim]Log : {nb_t} tâche(s) complétée(s) dans cette session[/dim]")


def verifier_reprise(path_projet):
    logger     = Logger(path_projet)
    incomplete = logger.derniere_tache_incomplete()

    if not incomplete:
        return logger, None

    tache  = incomplete["details"].get("tache", "?")
    numero = incomplete["details"].get("numero", "?")
    total  = incomplete["details"].get("total", "?")
    time   = incomplete.get("time", "?")

    separateur()
    console.print(f"\n[bold yellow]Session précédente détectée ![/bold yellow]")
    console.print(f"  Arrêtée à : Tâche [bold]{numero}/{total}[/bold]")
    console.print(f"  [dim]{tache}[/dim]")
    console.print(f"  Le : [dim]{time}[/dim]")

    if confirmer("Reprendre depuis cet endroit ?", defaut=True):
        ok("Reprise de la session précédente")
        return logger, incomplete
    else:
        info("Nouvelle session")
        logger.entrees = []
        logger._sauvegarder()
        return logger, None
