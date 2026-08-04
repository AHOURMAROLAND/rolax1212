# ============================================================
#  agent.py — Boucle principale et routing
#  rolax1212 v2.0.1 by Roland
# ============================================================

import sys
from pathlib import Path
from .ui          import console, ok, info, warn, err, separateur, confirmer
from .ui          import afficher_aide, banniere_session, afficher_audit
from .llm         import demander_conversation
from .projet      import lire_projet, afficher_structure, lire_task, executer
from .audit       import generer_rapport, corriger_bugs
from .task_parser import generer_task_md, afficher_et_valider, lire_description_fichier
from .generateur  import traiter, executer_tasks
from .frameworks  import detecter_framework, confirmer_framework, init_framework, choisir_framework, FRAMEWORKS
from .logger      import verifier_reprise
from .git_manager import commit_auto, init_git, afficher_statut, historique_git, push, commit_message_libre
from .config      import afficher_config, set_cle, supprimer_cle


def lancer(modele, path_str):
    info(f"Chargement du projet : {path_str}")
    path, fichiers = lire_projet(path_str)
    if path is None:
        sys.exit(1)

    ok(f"{len(fichiers)} fichier(s) chargé(s)")
    afficher_structure(path, fichiers)

    # ── Détection framework ──────────────────────────────────
    framework = None
    detecte   = detecter_framework(path, fichiers)

    if detecte:
        # Framework détecté via fichiers signatures → confirmation
        framework = confirmer_framework(detecte)
    else:
        # Aucun framework détecté → demande simple
        console.print()
        if confirmer("Ce projet utilise-t-il un framework ?", defaut=False):
            framework = choisir_framework()
        else:
            ok("Mode langage libre activé")
            framework = "aucun"

    historique = []

    # ── Vérification reprise session ─────────────────────────
    logger, reprise = verifier_reprise(path)

    # ── Audit automatique si projet existant ─────────────────
    fichiers_code = {k: v for k, v in fichiers.items()
                     if not k.endswith(".md") and not k.endswith(".txt")}
    if fichiers_code and not reprise:
        info("Projet existant — audit automatique...")
        _faire_audit(path, fichiers, modele, historique)

    # ── Reprise ou Task.md ───────────────────────────────────
    if reprise:
        task_path, task_contenu = lire_task(path)
        if task_contenu:
            from .projet import extraire_taches
            restantes = logger.taches_restantes(extraire_taches(task_contenu))
            if restantes:
                info(f"{len(restantes)} tâche(s) restante(s)")
                executer_tasks(task_path, task_contenu, path, modele,
                               fichiers, historique, logger=logger,
                               taches_filtrees=restantes, framework=framework)
    else:
        task_path, task_contenu = lire_task(path)
        if task_contenu:
            console.print(f"\n[bold yellow]Task.md détecté ![/bold yellow]")
            if confirmer("Exécuter les tâches du Task.md maintenant ?", defaut=False):
                executer_tasks(task_path, task_contenu, path, modele,
                               fichiers, historique, logger=logger, framework=framework)

    banniere_session(modele, path)
    logger.afficher_resume()

    while True:
        try:
            separateur()
            commande = console.input("\n[bold green]Toi >[/bold green] ").strip()
            if not commande:
                continue
            _router(commande, path, modele, fichiers, historique, framework, logger)
        except KeyboardInterrupt:
            console.print("\n")
            if confirmer("Quitter rolax1212 ?", defaut=False):
                logger.session_fin()
                console.print("\n[bold cyan]rolax1212 — À bientôt ![/bold cyan]\n")
                sys.exit(0)
            else:
                console.print("[dim]Reprise...[/dim]")
        except EOFError:
            break


# ============================================================
#  ROUTING
# ============================================================
def _router(commande, path, modele, fichiers, historique, framework, logger):
    cmd = commande.lower().strip()

    if cmd in ["exit", "quit", "bye", "quitte"]:
        logger.session_fin()
        console.print("\n[bold cyan]rolax1212 — À bientôt ![/bold cyan]\n")
        sys.exit(0)

    if cmd in ["aide", "help"]:
        afficher_aide()
        return

    if cmd in ["structure", "arbre", "tree", "ls"]:
        afficher_structure(path, fichiers)
        return

    if cmd in ["audit", "check", "cuf", "rapport"]:
        _faire_audit(path, fichiers, modele, historique)
        return

    if cmd in ["task", "tasks", "taches", "tâches"]:
        task_path, task_contenu = lire_task(path)
        if task_contenu:
            executer_tasks(task_path, task_contenu, path, modele,
                           fichiers, historique, logger=logger, framework=framework)
        else:
            warn("Aucun Task.md trouvé. Utilise 'plan' pour en créer un.")
        return

    # ── Init framework ──
    if cmd.startswith("init"):
        reste = commande[4:].strip().lower()
        cle   = reste if reste in FRAMEWORKS else None
        if not cle:
            cle = choisir_framework()
        init_framework(cle, path)
        _, nouveaux = lire_projet(str(path))
        fichiers.update(nouveaux)
        return

    # ── Changer framework ──
    if cmd in ["framework", "fw"]:
        framework = choisir_framework()
        return

    # ── Git ──
    if cmd in ["git", "commit"]:
        commit_auto(path, modele, historique)
        return

    if cmd in ["git status", "git st"]:
        afficher_statut(path)
        return

    if cmd in ["git log"]:
        historique_git(path)
        return

    if cmd in ["git push"]:
        push(path)
        return

    if cmd in ["git init"]:
        init_git(path)
        return

    # ── Config / clés API ──
    if cmd in ["config", "configuration", "cles", "clés"]:
        afficher_config()
        return

    if cmd.startswith("cle ") or cmd.startswith("clé "):
        # cle groq sk-...   ou   cle groq supprimer
        parties = commande.split()
        if len(parties) >= 3:
            provider_id = parties[1].lower()
            valeur      = parties[2]
            if valeur.lower() in ["del", "delete", "supprimer", "remove"]:
                supprimer_cle(provider_id)
                ok(f"Clé {provider_id} supprimée.")
            else:
                set_cle(provider_id, valeur)
                ok(f"Clé {provider_id} sauvegardée.")
        else:
            warn("Usage : cle <provider> <valeur>  ou  cle <provider> supprimer")
        return

    # ── Changer provider ──
    if cmd in ["provider", "fournisseur", "connexion"]:
        from .llm import choisir_provider_et_modele
        choisir_provider_et_modele()
        return

    if cmd.startswith("commit "):
        message = commande[7:].strip().strip('"').strip("'")
        commit_message_libre(path, message)
        return

    # ── Plan ──
    if cmd.startswith("plan"):
        description = commande[4:].strip()

        # Fichier .txt
        if description.endswith(".txt"):
            p = Path(description) if Path(description).exists() else Path(path) / description
            description = lire_description_fichier(p) or description

        # Saisie interactive
        if not description:
            console.print("[dim]Décris ton projet (langage libre). Ligne vide pour terminer.[/dim]\n")
            lignes = []
            while True:
                l = console.input("  ").strip()
                if not l:
                    break
                lignes.append(l)
            description = "\n".join(lignes)

        if not description:
            warn("Aucune description fournie.")
            return

        contenu = generer_task_md(description, modele, fichiers, path)
        if contenu and afficher_et_valider(contenu, path):
            task_path, task_contenu = lire_task(path)
            if task_contenu and confirmer("Exécuter maintenant ?", defaut=False):
                executer_tasks(task_path, task_contenu, path, modele,
                               fichiers, historique, logger=logger, framework=framework)
        return

    # ── Lis ──
    if cmd.startswith("lis ") or cmd.startswith("affiche "):
        nom    = commande.split(" ", 1)[1].strip()
        chemin = Path(path) / nom
        if chemin.exists():
            from .ui import code as afficher_code
            from .projet import EXTENSIONS_CODE
            afficher_code(chemin.read_text(encoding="utf-8"), EXTENSIONS_CODE.get(chemin.suffix, "text"))
        else:
            err(f"Fichier '{nom}' introuvable.")
        return

    # ── Exec ──
    if cmd.startswith("exec ") or cmd.startswith("run "):
        nom    = commande.split(" ", 1)[1].strip()
        chemin = Path(path) / nom
        if chemin.exists():
            code_ret, stdout, stderr = executer(chemin, path)
            if stdout: console.print(f"[dim]Sortie :[/dim]\n{stdout}")
            if stderr: console.print(f"[red]Erreur :[/red]\n{stderr}")
        else:
            err(f"Fichier '{nom}' introuvable.")
        return

    # ── LLM ──
    traiter(commande, path, modele, fichiers, historique, framework=framework)


# ============================================================
#  AUDIT
# ============================================================
def _faire_audit(path, fichiers, modele, historique):
    rapport = generer_rapport(fichiers, modele)
    bugs    = rapport.get("check", [])
    if bugs:
        info(f"{len(bugs)} bug(s) — correction automatique...")
        rapport = corriger_bugs(rapport, path, fichiers, modele)
    afficher_audit(rapport)
    historique.append({
        "role": "assistant",
        "content": f"Audit : {len(bugs)} bugs, {len(rapport.get('update',[]))} updates, {len(rapport.get('future',[]))} futures."
    })
