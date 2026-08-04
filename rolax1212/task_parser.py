# ============================================================
#  task_parser.py — Langage libre → Task.md
#  rolax1212 v2.0.1 by Roland
# ============================================================

import re
from datetime import datetime
from pathlib  import Path
from .ui  import console, ok, info, warn, code, confirmer, separateur
from .llm import demander

PROMPT = """Tu es un expert en développement logiciel.
L'utilisateur décrit son projet en langage libre.

Description :
\"\"\"{description}\"\"\"

Contexte existant :
{contexte}

Génère un Task.md structuré. Format EXACT :

```markdown
# [Nom du projet] — Plan rolax1212 v2.0.1

## Contexte
[Résumé en 1-2 phrases]

## Stack technique
[Langage, framework, base de données]

## Tâches
- [ ] Tâche 1 précise et actionnable
- [ ] Tâche 2
...

## Généré le
{date}
```

Règles :
- Chaque tâche = 1 fichier ou 1 fonctionnalité précise
- Maximum 15 tâches
- Ordonnées logiquement (config → models → views → templates → style)
- Si framework Django : utilise les bons chemins (restaurant/models.py, templates/restaurant/menu.html)
- PHP par défaut si non précisé
"""


def generer_task_md(description, modele, fichiers=None, path_projet=None):
    from .projet import construire_contexte
    contexte = construire_contexte(fichiers) if fichiers else "Nouveau projet."
    prompt   = PROMPT.format(
        description=description,
        contexte=contexte,
        date=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    info("Génération du Task.md...")
    reponse = demander([{"role": "user", "content": prompt}], modele, stream=True, timeout=120)
    if not reponse:
        warn("Impossible de générer le Task.md.")
        return None
    return _extraire(reponse)


def _extraire(reponse):
    m = re.search(r"```markdown\n(.*?)```", reponse, re.DOTALL)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"(# .+)", reponse, re.DOTALL)
    if m2:
        return m2.group(1).strip()
    return reponse.strip()


def afficher_et_valider(contenu, path_projet):
    separateur()
    console.print("\n[bold cyan]Task.md généré :[/bold cyan]\n")
    code(contenu, "markdown")
    separateur()

    if confirmer("\nValider et sauvegarder ce Task.md ?", defaut=True):
        chemin = Path(path_projet) / "Task.md"
        chemin.write_text(contenu, encoding="utf-8")
        ok(f"Task.md sauvegardé")
        return True
    warn("Task.md non sauvegardé.")
    return False


def lire_description_fichier(chemin):
    try:
        return Path(chemin).read_text(encoding="utf-8")
    except Exception:
        return None
