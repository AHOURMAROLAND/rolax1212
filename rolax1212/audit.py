# ============================================================
#  audit.py — Rapport C/U/F
#  rolax1212 v2.0.1 by Roland
# ============================================================

import json
import re
from .ui  import console, ok, info, warn, err, afficher_audit
from .llm import demander

PROMPT_AUDIT = """Analyse ce projet et génère un rapport JSON structuré.

{contexte}

Réponds UNIQUEMENT avec ce JSON valide (rien d'autre) :
{{
  "check":  [{{"fichier": "nom.php", "probleme": "description courte", "corrige": false}}],
  "update": ["amélioration concrète"],
  "future": ["fonctionnalité à ajouter"]
}}

Règles :
- "check"  : bugs réels (syntaxe cassée, sécurité critique, logique erronée)
- "update" : améliorations de qualité
- "future" : nouvelles fonctionnalités utiles
- Maximum 5 items par section
- Réponds UNIQUEMENT avec le JSON
"""


def generer_rapport(fichiers, modele):
    from .projet import construire_contexte
    if not fichiers:
        return {"check": [], "update": [], "future": []}

    info("Analyse du projet en cours...")
    contexte = construire_contexte(fichiers)
    messages = [{"role": "user", "content": PROMPT_AUDIT.format(contexte=contexte)}]
    reponse  = demander(messages, modele, stream=False, timeout=120)

    if not reponse:
        warn("Impossible d'obtenir le rapport.")
        return {"check": [], "update": [], "future": []}

    return _parser(reponse)


def _parser(reponse):
    match = re.search(r'\{.*\}', reponse, re.DOTALL)
    try:
        data = json.loads(match.group(0) if match else reponse.strip())
        return {"check": data.get("check", []), "update": data.get("update", []), "future": data.get("future", [])}
    except Exception:
        return {"check": [], "update": [], "future": []}


def corriger_bugs(rapport, path_projet, fichiers, modele):
    from .projet import sauvegarder, extraire_blocs
    from pathlib import Path

    for i, bug in enumerate(rapport.get("check", [])):
        nom = bug.get("fichier", "")
        if not nom or nom == "?":
            continue
        chemin = Path(path_projet) / nom
        if not chemin.exists():
            continue

        info(f"Correction de {nom}...")
        contenu = chemin.read_text(encoding="utf-8")
        lang    = chemin.suffix.lstrip(".")
        prompt  = (f"Bug dans {lang.upper()} : {bug.get('probleme','')}\n\n"
                   f"```{lang}\n{contenu}\n```\n\n"
                   f"Retourne UNIQUEMENT le code corrigé dans ```{lang} ... ```. Pas d'explication.")

        rep = demander([{"role": "user", "content": prompt}], modele, stream=False, timeout=120)
        if rep:
            blocs = extraire_blocs(rep)
            if blocs and len(blocs[0]["code"]) > 20:
                sauvegarder(chemin, blocs[0]["code"])
                fichiers[nom] = blocs[0]["code"]
                rapport["check"][i]["corrige"] = True

    return rapport
