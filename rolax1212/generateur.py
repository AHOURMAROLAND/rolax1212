# ============================================================
#  generateur.py — Génération et vérification de code
#  rolax1212 v2.0.1 by Roland
# ============================================================

import re
from pathlib import Path
from .ui     import console, ok, info, warn, err, separateur, confirmer
from .ui     import projet_termine, projet_termine_avertissement
from .llm    import demander
from .projet import extraire_blocs, sauvegarder, executer

MODELES_FAIBLES = ["1.5b", "0.5b", "1b"]

FICHIERS_DJANGO = [
    "models.py", "views.py", "urls.py", "forms.py", "admin.py",
    "apps.py", "serializers.py", "signals.py", "settings.py",
    "wsgi.py", "asgi.py", "manage.py"
]

MOTS_CREATION = [
    "crée", "cree", "créer", "create", "génère", "genere",
    "écris", "ecris", "ajoute", "fais", "implemente", "implémente",
    "développe", "developpe", "fichier", "classe", "script",
    "module", "fonction", "page", "formulaire", "table",
    "connexion", "login", "dashboard", "controller", "model", "view"
]

PROMPT_SYSTEME = """Tu es rolax1212, un agent de développement expert.
Tu travailles sur ce projet :

{contexte}
{prompt_fw}

RÈGLES ABSOLUES :
1. Pour CHAQUE fichier, écris sur sa propre ligne :
   FICHIER: chemin/nom_exact.ext
   Puis le bloc de code :
   ```php
   ... code complet ...
   ```
2. Code 100% fonctionnel — JAMAIS de placeholder ou TODO
3. PHP : PDO, prepared statements, htmlspecialchars, password_hash
4. Java : PascalCase classes, camelCase méthodes
5. Réponds en français sauf pour le code

EXEMPLE :
FICHIER: restaurant/models.py
```python
from django.db import models
class Produit(models.Model):
    nom = models.CharField(max_length=100)
```
"""


def est_demande_creation(cmd):
    return any(m in cmd.lower() for m in MOTS_CREATION)


def traiter(commande, path_projet, modele, fichiers, historique, auto=False, framework=None):
    from .projet import construire_contexte

    contexte   = construire_contexte(fichiers)
    creation   = est_demande_creation(commande)
    est_faible = any(p in modele for p in MODELES_FAIBLES)

    # Nom de fichier mentionné dans la commande
    nom_cmd = None
    m = re.search(r"([a-zA-Z0-9_\-/]+\.(?:php|py|js|java|html|css|sql|ts|sh|md|dart))", commande.lower())
    if m:
        nom_cmd = m.group(1)

    # Prompt framework
    prompt_fw = ""
    if framework and framework != "aucun":
        try:
            from .frameworks import prompt_framework
            prompt_fw = prompt_framework(framework)
        except Exception:
            pass

    system = PROMPT_SYSTEME.format(contexte=contexte, prompt_fw=prompt_fw)
    historique.append({"role": "user", "content": commande})
    messages = [{"role": "system", "content": system}] + historique

    console.print(f"\n[dim]Traitement en cours...[/dim]")

    if creation:
        reponse = demander(messages, modele, stream=True, timeout=300)
    else:
        from .llm import demander_conversation
        reponse = demander_conversation(messages, modele)

    if not reponse:
        err("Pas de réponse du LLM.")
        historique.pop()
        return

    historique.append({"role": "assistant", "content": reponse})

    blocs = extraire_blocs(reponse)
    if not blocs or not creation:
        return

    fichiers_crees = []
    for i, bloc in enumerate(blocs):
        nom = bloc["nom"] or nom_cmd
        if not nom:
            ext_map = {
                "python": ".py", "php": ".php", "java": ".java",
                "javascript": ".js", "typescript": ".ts",
                "html": ".html", "css": ".css", "sql": ".sql",
                "bash": ".sh", "markdown": ".md", "dart": ".dart"
            }
            ext  = ext_map.get(bloc["lang"], ".txt")
            mots = commande.lower().split()
            nom  = next((mo for mo in mots if "." in mo and len(mo) > 3), f"fichier_{i+1}{ext}")

        if not auto:
            console.print(f"\n[bold yellow]Fichier à créer : {nom}[/bold yellow]")
            if not confirmer("Créer ce fichier ?"):
                info("Ignoré.")
                continue

        chemin = Path(path_projet) / nom
        sauvegarder(chemin, bloc["code"])
        fichiers[nom] = bloc["code"]
        fichiers_crees.append(chemin)

    if not fichiers_crees:
        return

    # Vérification
    separateur()
    info("Vérification automatique...")
    tous_ok = True

    for chemin in fichiers_crees:
        success = _verifier(chemin, modele, historique, path_projet, est_faible)
        if success:
            ok(f"{chemin.name} — OK")
        else:
            warn(f"{chemin.name} — vérification manuelle requise")
            tous_ok = False

    separateur()
    if tous_ok:
        projet_termine([str(f) for f in fichiers_crees])
    else:
        projet_termine_avertissement([str(f) for f in fichiers_crees])


def _verifier(chemin, modele, historique, cwd, est_faible):
    ext = chemin.suffix
    nom = chemin.name

    if est_faible:
        ok(f"{nom} — sauvegardé")
        return True

    # Fichiers Django, templates, statiques → pas d'exécution
    if nom in FICHIERS_DJANGO:
        ok(f"{nom} — sauvegardé (fichier framework)")
        return True

    if ext in [".html", ".css", ".sql", ".md", ".txt", ".dart", ".yaml", ".yml"]:
        ok(f"{nom} — sauvegardé")
        return True

    # Fichiers exécutables autonomes
    if ext in [".py", ".js", ".sh"]:
        return _verifier_execution(chemin, modele, historique, cwd)

    # Autres : vérification syntaxique LLM
    return _verifier_syntaxe(chemin, ext, modele, historique)


def _verifier_execution(chemin, modele, historique, cwd):
    MAX = 3
    for tentative in range(1, MAX + 1):
        info(f"Exécution — tentative {tentative}/{MAX}...")
        code_ret, stdout, stderr = executer(chemin, cwd)

        if stderr and code_ret != 0:
            warn(f"Erreur :\n{stderr[:300]}")
            contenu = chemin.read_text(encoding="utf-8")
            lang    = chemin.suffix.lstrip(".")
            prompt  = (f"Erreur dans ce code :\n```{lang}\n{contenu}\n```\n"
                       f"Erreur : ```\n{stderr[:500]}\n```\n"
                       f"Retourne UNIQUEMENT le code corrigé dans ```{lang} ... ```. Pas d'explication.")
            historique.append({"role": "user", "content": prompt})
            rep = demander(historique, modele, stream=False, timeout=120)
            if not rep:
                break
            historique.append({"role": "assistant", "content": rep})
            blocs = extraire_blocs(rep)
            if blocs:
                chemin.write_text(blocs[0]["code"], encoding="utf-8")
        else:
            if stdout:
                console.print(f"[dim]Sortie :[/dim]\n{stdout[:300]}")
            return True

    err(f"Échec après {MAX} tentatives.")
    return False


def _verifier_syntaxe(chemin, ext, modele, historique):
    contenu = chemin.read_text(encoding="utf-8")
    lang    = ext.lstrip(".")
    prompt  = (f"Vérifie ce code {lang.upper()} (syntaxe cassée uniquement) :\n\n"
               f"```{lang}\n{contenu}\n```\n\n"
               f"Si correct → réponds : CODE OK\n"
               f"Si erreur → code corrigé dans ```{lang} ... ``` + une ligne d'explication.")
    historique.append({"role": "user", "content": prompt})
    rep = demander(historique, modele, stream=False, timeout=90)
    if not rep:
        return True
    historique.append({"role": "assistant", "content": rep})
    if "CODE OK" in rep.upper():
        return True
    blocs = extraire_blocs(rep)
    if blocs and len(blocs[0]["code"]) > 20:
        chemin.write_text(blocs[0]["code"], encoding="utf-8")
        ok(f"{chemin.name} — correction appliquée")
    return True


def executer_tasks(path_task, contenu_task, path_projet, modele, fichiers,
                   historique, logger=None, taches_filtrees=None, framework=None):
    import time
    from .projet import extraire_taches, marquer_tache_faite
    from .ui     import titre

    # Délai entre tâches pour éviter le rate limit Groq (30 req/min)
    delai = 4 if modele.startswith("groq:") else 0

    titre("Exécution des tâches depuis Task.md")
    taches = taches_filtrees or extraire_taches(contenu_task)

    if not taches:
        warn("Aucune tâche trouvée dans Task.md")
        warn("Vérifie que chaque tâche commence par '- [ ] ' (avec espace après ])")
        return

    console.print(f"\n[cyan]{len(taches)} tâche(s) à réaliser :[/cyan]")
    for i, t in enumerate(taches, 1):
        console.print(f"  {i}. {t}")

    separateur()

    for i, tache in enumerate(taches, 1):
        console.print(f"\n[bold cyan]── Tâche {i}/{len(taches)} ──[/bold cyan]")
        console.print(f"[yellow]{tache}[/yellow]\n")

        if logger:
            logger.tache_debut(i, len(taches), tache)

        # Historique limité à 4 échanges pour éviter le rate limit tokens
        if len(historique) > 4:
            historique[:] = historique[-4:]

        traiter(tache, path_projet, modele, fichiers, historique, auto=True, framework=framework)
        marquer_tache_faite(path_task, tache)

        if logger:
            logger.tache_fin(i, len(taches), tache)

        separateur()

        if delai and i < len(taches):
            console.print(f"[dim]Pause {delai}s (limite Groq)...[/dim]")
            time.sleep(delai)

    ok("Toutes les tâches du Task.md ont été traitées !")
