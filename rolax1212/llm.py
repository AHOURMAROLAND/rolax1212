# ============================================================
#  llm.py — Connexion Ollama
#  rolax1212 v2.0.1 by Roland
# ============================================================

import json
import requests
from .ui import console, ok, info, warn, err

OLLAMA_URL  = "http://localhost:11434/api/chat"
OLLAMA_TAGS = "http://localhost:11434/api/tags"

MODELES_PUISSANTS = ["gpt-oss", "llama3", "mistral", "mixtral", "70b", "120b"]
MODELES_LEGERS    = ["1.5b", "0.5b", "1b", "3b"]


def ollama_actif():
    try:
        requests.get(OLLAMA_TAGS, timeout=3)
        return True
    except Exception:
        return False


def lister_modeles():
    try:
        r = requests.get(OLLAMA_TAGS, timeout=5)
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


def choisir_modele():
    info("Connexion à Ollama...")

    if not ollama_actif():
        err("Ollama ne répond pas.")
        err("Lance Ollama d'abord : ollama serve")
        raise SystemExit(1)

    ok("Ollama actif")
    modeles = lister_modeles()

    if not modeles:
        err("Aucun modèle installé.")
        err("Lance : ollama pull qwen2.5:1.5b")
        raise SystemExit(1)

    console.print("\n[bold cyan]Modèles disponibles :[/bold cyan]")
    for i, m in enumerate(modeles, 1):
        if any(p in m for p in MODELES_PUISSANTS):
            tag = "[yellow]★ puissant[/yellow]  [dim](recommandé pour le code)[/dim]"
        elif any(p in m for p in MODELES_LEGERS):
            tag = "[green]⚡ rapide[/green]   [dim](recommandé pour conversation)[/dim]"
        else:
            tag = "[dim]standard[/dim]"
        console.print(f"  [bold]{i}[/bold]. {m}  {tag}")

    console.print()
    choix = console.input("[cyan]Choisis un modèle (numéro ou nom) [1]: [/cyan]").strip() or "1"

    if choix.isdigit():
        idx = int(choix) - 1
        modele = modeles[idx] if 0 <= idx < len(modeles) else modeles[0]
    else:
        modele = next((m for m in modeles if choix.lower() in m.lower()), modeles[0])

    ok(f"Modèle sélectionné : [bold]{modele}[/bold]")
    return modele


def demander(messages, modele, stream=True, timeout=300):
    payload = {
        "model":    modele,
        "messages": messages,
        "stream":   stream,
        "options":  {"temperature": 0.2, "num_predict": 4096, "num_ctx": 8192}
    }
    try:
        if stream:
            return _stream(payload, timeout)
        else:
            r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
            return r.json().get("message", {}).get("content", "")
    except requests.exceptions.ConnectionError:
        err("Ollama ne répond pas.")
        return None
    except requests.exceptions.Timeout:
        err(f"Timeout {timeout}s — essaie un modèle plus léger.")
        return None
    except Exception as e:
        err(f"Erreur LLM : {e}")
        return None


def demander_conversation(messages, modele):
    """Utilise toujours le modèle principal — pas de fallback."""
    return demander(messages, modele, stream=True, timeout=300)


def _stream(payload, timeout=300):
    reponse        = ""
    affiche_entete = False
    est_dans_code  = False

    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=timeout) as r:
            for ligne in r.iter_lines():
                if not ligne:
                    continue
                try:
                    data  = json.loads(ligne)
                    token = data.get("message", {}).get("content", "")
                    reponse += token

                    # Détecte blocs de code — ne pas afficher le code brut
                    if "```" in reponse[-20:]:
                        est_dans_code = not est_dans_code

                    if not est_dans_code and "```" not in token:
                        if not affiche_entete:
                            console.print("\n[bold cyan]Jarvis >[/bold cyan] ", end="")
                            affiche_entete = True
                        print(token, end="", flush=True)

                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
        if affiche_entete:
            print()
    except requests.exceptions.Timeout:
        print()
        err("Timeout — modèle trop lent.")
    except Exception as e:
        print()
        err(f"Stream interrompu : {e}")

    return reponse or None
