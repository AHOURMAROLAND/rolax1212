# ============================================================
#  config.py — Configuration, clés API et variables système
#  rolax1212 v4.2.0 by Roland
# ============================================================

import os
import sys
import json
import platform
import subprocess
from pathlib import Path

CONFIG_DIR  = Path.home() / ".rolax1212"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Noms des variables d'environnement système par provider
ENV_VARS = {
    "groq":     "GROQ_API_KEY",
    "gemini":   "GEMINI_API_KEY",
    "claude":   "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openai":   "OPENAI_API_KEY",
}


# ============================================================
#  FICHIER CONFIG JSON
# ============================================================
def charger_config() -> dict:
    """Charge la config depuis ~/.rolax1212/config.json."""
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def sauvegarder_config(config: dict):
    """Sauvegarde la config dans ~/.rolax1212/config.json."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        from .ui import warn
        warn(f"Impossible de sauvegarder la config : {e}")


# ============================================================
#  RESOLUTION DES CLES — priorité : système > config.json
# ============================================================
def get_cle(provider: str) -> str:
    """
    Retourne la clé API d'un provider.
    Ordre de priorité :
      1. Variable d'environnement système (ex: GROQ_API_KEY)
      2. Fichier ~/.rolax1212/config.json
    """
    # 1. Variable système
    var_sys = ENV_VARS.get(provider)
    if var_sys:
        val = os.environ.get(var_sys, "")
        if val:
            return val

    # 2. Fichier config
    return charger_config().get("cles", {}).get(provider, "")


def set_cle(provider: str, cle: str):
    """Sauvegarde une clé API dans config.json."""
    config = charger_config()
    if "cles" not in config:
        config["cles"] = {}
    config["cles"][provider] = cle
    sauvegarder_config(config)


def supprimer_cle(provider: str):
    """Supprime la clé API d'un provider du fichier config."""
    config = charger_config()
    if "cles" in config and provider in config["cles"]:
        del config["cles"][provider]
        sauvegarder_config(config)


def get_provider_actif() -> str:
    return charger_config().get("dernier_provider", "ollama")


def get_modele_actif() -> str:
    return charger_config().get("dernier_modele", "")


# ============================================================
#  ECRITURE DANS LES VARIABLES SYSTEME
# ============================================================
def _ecrire_var_systeme(nom_var: str, valeur: str) -> bool:
    """
    Écrit une variable d'environnement de façon persistante.
    - Windows : SETX (variables utilisateur permanentes)
    - Linux/macOS : ajoute dans ~/.bashrc et ~/.zshrc
    """
    systeme = platform.system()

    try:
        if systeme == "Windows":
            # SETX écrit dans le registre utilisateur — persistant après redémarrage
            subprocess.run(
                ["setx", nom_var, valeur],
                capture_output=True, text=True, timeout=10
            )
            # Aussi dans l'environnement du processus actuel
            os.environ[nom_var] = valeur
            return True

        else:
            # Linux / macOS — ajoute dans les fichiers de profil shell
            ligne = f'\nexport {nom_var}="{valeur}"\n'
            profils = []

            for rc in [".bashrc", ".zshrc", ".profile", ".bash_profile"]:
                p = Path.home() / rc
                if p.exists():
                    profils.append(p)

            if not profils:
                # Crée .bashrc si aucun fichier de profil trouvé
                profils = [Path.home() / ".bashrc"]

            for profil in profils:
                contenu = profil.read_text(encoding="utf-8") if profil.exists() else ""
                # Évite les doublons
                if f"export {nom_var}=" not in contenu:
                    with profil.open("a", encoding="utf-8") as f:
                        f.write(ligne)

            # Actif pour le processus courant
            os.environ[nom_var] = valeur
            return True

    except Exception:
        return False


def ecrire_cles_systeme(provider: str, cle: str) -> bool:
    """Écrit la clé d'un provider dans les variables système."""
    var_sys = ENV_VARS.get(provider)
    if not var_sys:
        return False
    return _ecrire_var_systeme(var_sys, cle)


# ============================================================
#  SETUP INITIAL — appelé au premier lancement
# ============================================================
def setup_initial():
    """
    Vérifie si rolax1212 est configuré.
    Si c'est le premier lancement ou si des clés manquent dans
    les variables système, propose de les configurer.
    Retourne True si setup effectué ou déjà OK.
    """
    from .ui import console, ok, info, warn, separateur, confirmer, titre

    config = charger_config()

    # Marque le premier lancement
    premier_lancement = not config.get("setup_fait", False)

    if not premier_lancement:
        return False  # Déjà configuré — rien à faire

    separateur()
    titre("Configuration initiale de rolax1212")
    console.print(
        "\n[dim]rolax1212 peut sauvegarder tes clés API directement dans les\n"
        "variables d'environnement système pour ne jamais avoir à les\n"
        "ressaisir, même après redémarrage.[/dim]\n"
    )

    systeme = platform.system()
    if systeme == "Windows":
        console.print("[dim]Méthode : SETX (variables utilisateur Windows — permanentes)[/dim]")
    else:
        console.print(f"[dim]Méthode : export dans ~/.bashrc / ~/.zshrc[/dim]")

    console.print()

    if not confirmer("Configurer les variables système maintenant ?", defaut=True):
        info("Tu pourras configurer plus tard avec la commande 'config'.")
        config["setup_fait"] = True
        sauvegarder_config(config)
        return False

    _assistant_configuration(config)
    config["setup_fait"] = True
    sauvegarder_config(config)
    return True


def _assistant_configuration(config):
    """Assistant interactif de configuration des clés API."""
    from .ui import console, ok, info, warn, separateur

    providers_externes = {
        "groq":     ("Groq",            "groq.com/keys",                    "gsk_..."),
        "gemini":   ("Gemini (Google)", "aistudio.google.com/apikey",       "AIza..."),
        "claude":   ("Claude (Anthropic)", "console.anthropic.com/settings/keys", "sk-ant-..."),
        "deepseek": ("DeepSeek",        "platform.deepseek.com/api_keys",   "sk-..."),
        "openai":   ("OpenAI",          "platform.openai.com/api-keys",     "sk-..."),
    }

    console.print("\n[bold cyan]Entre tes clés API (Entrée pour ignorer) :[/bold cyan]\n")

    for provider_id, (nom, url, exemple) in providers_externes.items():
        var_sys = ENV_VARS[provider_id]

        # Vérifie si déjà présente
        existante = os.environ.get(var_sys, "") or config.get("cles", {}).get(provider_id, "")
        if existante:
            masque = existante[:6] + "..." + existante[-4:]
            console.print(f"  [green]✓[/green] {nom:<20} [dim]{var_sys} déjà définie ({masque})[/dim]")
            continue

        console.print(f"  [cyan]{nom}[/cyan]  [dim]{url}[/dim]")
        console.print(f"  [dim]Variable système : {var_sys}  •  Format : {exemple}[/dim]")
        cle = console.input(f"  Clé API : ").strip()

        if cle:
            # Sauvegarde dans les variables système ET config.json
            succes_sys = ecrire_cles_systeme(provider_id, cle)
            set_cle(provider_id, cle)

            if succes_sys:
                ok(f"{nom} → {var_sys} définie en variable système")
            else:
                ok(f"{nom} → sauvegardée dans config.json")
        else:
            console.print(f"  [dim]Ignoré.[/dim]")

        console.print()

    separateur()
    console.print(
        "[bold green]Configuration terminée ![/bold green]\n"
        "[dim]Les clés sont dans tes variables système — rolax1212 les\n"
        "lira automatiquement à chaque lancement.[/dim]\n"
    )
    if platform.system() != "Windows":
        warn("Sur Linux/macOS : relance ton terminal ou fais 'source ~/.bashrc' pour activer.")


# ============================================================
#  AFFICHAGE CONFIG
# ============================================================
def afficher_config():
    """Affiche la config complète avec statut variables système."""
    from .ui import console, separateur, titre

    config  = charger_config()
    systeme = platform.system()

    titre("Configuration rolax1212")
    separateur()

    provider = config.get("dernier_provider", "non défini")
    modele   = config.get("dernier_modele",   "non défini")
    console.print(f"  [dim]Provider actif :[/dim] [cyan]{provider}[/cyan]")
    console.print(f"  [dim]Modèle actif   :[/dim] [cyan]{modele}[/cyan]")
    console.print(f"  [dim]Config file    :[/dim] [dim]{CONFIG_FILE}[/dim]")
    console.print(f"  [dim]Système        :[/dim] [dim]{systeme}[/dim]")

    console.print(f"\n  [bold cyan]Clés API :[/bold cyan]")
    console.print(f"  [dim]{'Provider':<12} {'Var système':<22} {'Système':<10} {'Config.json':<12}[/dim]")
    separateur()

    cles_json = config.get("cles", {})

    for provider_id, var_sys in ENV_VARS.items():
        val_sys  = os.environ.get(var_sys, "")
        val_json = cles_json.get(provider_id, "")

        statut_sys  = f"[green]✓ {val_sys[:6]}...{val_sys[-4:]}[/green]" if val_sys  else "[dim]—[/dim]"
        statut_json = f"[green]✓[/green]" if val_json else "[dim]—[/dim]"

        from .llm import PROVIDERS
        nom = PROVIDERS.get(provider_id, {}).get("nom", provider_id)
        console.print(f"  {nom:<20} {var_sys:<22} {statut_sys:<10} {statut_json}")

    separateur()
    console.print(
        "\n  [dim]Pour ajouter une clé : [cyan]cle <provider> <valeur>[/cyan]\n"
        "  Pour relancer le setup : [cyan]config setup[/cyan][/dim]\n"
    )
