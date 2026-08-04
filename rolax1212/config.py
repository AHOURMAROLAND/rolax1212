# ============================================================
#  config.py — Gestion configuration et clés API
#  rolax1212 v4.0.0 by Roland
# ============================================================

import json
from pathlib import Path

CONFIG_DIR  = Path.home() / ".rolax1212"
CONFIG_FILE = CONFIG_DIR / "config.json"


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


def get_cle(provider: str) -> str:
    """Retourne la clé API d'un provider, ou chaîne vide."""
    return charger_config().get("cles", {}).get(provider, "")


def set_cle(provider: str, cle: str):
    """Sauvegarde une clé API pour un provider."""
    config = charger_config()
    if "cles" not in config:
        config["cles"] = {}
    config["cles"][provider] = cle
    sauvegarder_config(config)


def supprimer_cle(provider: str):
    """Supprime la clé API d'un provider."""
    config = charger_config()
    if "cles" in config and provider in config["cles"]:
        del config["cles"][provider]
        sauvegarder_config(config)


def get_provider_actif() -> str:
    return charger_config().get("dernier_provider", "ollama")


def get_modele_actif() -> str:
    return charger_config().get("dernier_modele", "")


def afficher_config():
    """Affiche la config actuelle (clés masquées)."""
    from .ui import console, separateur, titre
    config = charger_config()

    titre("Configuration rolax1212")
    separateur()

    provider = config.get("dernier_provider", "non défini")
    modele   = config.get("dernier_modele",   "non défini")
    console.print(f"  [dim]Provider actif :[/dim] [cyan]{provider}[/cyan]")
    console.print(f"  [dim]Modèle actif   :[/dim] [cyan]{modele}[/cyan]")
    console.print(f"  [dim]Fichier config :[/dim] [dim]{CONFIG_FILE}[/dim]")

    cles = config.get("cles", {})
    if cles:
        console.print(f"\n  [dim]Clés API configurées :[/dim]")
        for p, k in cles.items():
            masque = k[:6] + "..." + k[-4:] if len(k) > 10 else "***"
            console.print(f"    [green]✓[/green]  {p:<12} [dim]{masque}[/dim]")
    else:
        console.print(f"\n  [dim]Aucune clé API sauvegardée.[/dim]")

    separateur()
