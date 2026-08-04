# ============================================================
#  llm.py — Routeur universel multi-providers
#  rolax1212 v4.0.0 by Roland
# ============================================================

import json
import os
import requests
from .ui     import console, ok, info, warn, err
from .config import charger_config, sauvegarder_config, get_cle, set_cle, ENV_VARS

# ── URLs ────────────────────────────────────────────────────
OLLAMA_URL  = "http://localhost:11434/api/chat"
OLLAMA_TAGS = "http://localhost:11434/api/tags"

# ── Catalogue providers ──────────────────────────────────────
PROVIDERS = {
    "ollama": {
        "nom":     "Ollama (local)",
        "icone":   "🦙",
        "couleur": "green",
        "url":     OLLAMA_URL,
        "cle":     False,   # pas de clé API nécessaire
        "modeles": [],      # dynamique via API
        "modeles_defaut": ["qwen2.5:7b", "llama3:8b", "mistral:7b", "qwen2.5:1.5b"],
    },
    "groq": {
        "nom":     "Groq",
        "icone":   "⚡",
        "couleur": "yellow",
        "url":     "https://api.groq.com/openai/v1/chat/completions",
        "cle":     True,
        "modeles": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        "modeles_defaut": ["llama-3.3-70b-versatile"],
    },
    "gemini": {
        "nom":     "Gemini (Google)",
        "icone":   "✨",
        "couleur": "cyan",
        "url":     "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "cle":     True,
        "modeles": [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
        "modeles_defaut": ["gemini-2.0-flash"],
    },
    "claude": {
        "nom":     "Claude (Anthropic)",
        "icone":   "🧠",
        "couleur": "magenta",
        "url":     "https://api.anthropic.com/v1/messages",
        "cle":     True,
        "modeles": [
            "claude-opus-4-5",
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "claude-3-5-sonnet-20241022",
        ],
        "modeles_defaut": ["claude-sonnet-4-5"],
    },
    "deepseek": {
        "nom":     "DeepSeek",
        "icone":   "🔍",
        "couleur": "blue",
        "url":     "https://api.deepseek.com/chat/completions",
        "cle":     True,
        "modeles": [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-reasoner",
        ],
        "modeles_defaut": ["deepseek-chat"],
    },
    "openai": {
        "nom":     "OpenAI",
        "icone":   "🤖",
        "couleur": "white",
        "url":     "https://api.openai.com/v1/chat/completions",
        "cle":     True,
        "modeles": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "modeles_defaut": ["gpt-4o-mini"],
    },
}

# Provider et modèle actifs pour la session
_provider_actif = "ollama"
_modele_actif   = ""


# ============================================================
#  SELECTION PROVIDER + MODELE
# ============================================================
def choisir_provider_et_modele():
    """
    Flow de démarrage :
    1. Propose la liste des providers
    2. Si clé requise → vérifie config ou demande saisie
    3. Liste les modèles du provider
    4. Retourne (provider, modele)
    """
    global _provider_actif, _modele_actif

    config = charger_config()

    # ── Choix provider ───────────────────────────────────────
    console.print("\n[bold cyan]Choisis ton provider LLM :[/bold cyan]\n")
    items = list(PROVIDERS.items())

    for i, (cle, p) in enumerate(items, 1):
        cle_ok = ""
        if p["cle"]:
            a_cle = bool(config.get("cles", {}).get(cle))
            cle_ok = "  [green]✓ clé configurée[/green]" if a_cle else "  [dim]clé requise[/dim]"
        else:
            # Vérifie si Ollama tourne
            if ollama_actif():
                cle_ok = "  [green]✓ actif[/green]"
            else:
                cle_ok = "  [red]✗ non détecté[/red]"

        console.print(
            f"  [bold]{i}[/bold]. [{p['couleur']}]{p['icone']} {p['nom']}[/{p['couleur']}]{cle_ok}"
        )

    console.print()
    choix = console.input("[cyan]Choix [1] : [/cyan]").strip() or "1"
    idx   = (int(choix) - 1) if choix.isdigit() else 0
    idx   = max(0, min(idx, len(items) - 1))

    provider_cle, provider = items[idx]
    ok(f"Provider : [{provider['couleur']}]{provider['icone']} {provider['nom']}[/{provider['couleur']}]")

    # ── Clé API ──────────────────────────────────────────────
    if provider["cle"]:
        cle_api = get_cle(provider_cle)
        if not cle_api:
            var_sys = ENV_VARS.get(provider_cle, "")
            console.print(f"\n[yellow]Clé API {provider['nom']} requise.[/yellow]")
            if var_sys:
                console.print(f"[dim]Tu peux aussi définir la variable système : {var_sys}[/dim]")
            cle_api = console.input(f"[cyan]Entre ta clé API : [/cyan]").strip()
            if not cle_api:
                err("Clé vide — abandon.")
                raise SystemExit(1)
            # Sauvegarde dans variables système + config.json
            from .config import ecrire_cles_systeme
            ecrire_cles_systeme(provider_cle, cle_api)
            set_cle(provider_cle, cle_api)
            ok("Clé sauvegardée en variable système et config.json")
        else:
            masque = cle_api[:6] + "..." + cle_api[-4:]
            # Indique la source
            var_sys = ENV_VARS.get(provider_cle, "")
            source  = f"[dim](var. système {var_sys})[/dim]" if os.environ.get(var_sys) else "[dim](config.json)[/dim]"
            ok(f"Clé API chargée : [dim]{masque}[/dim]  {source}")
    else:
        # Ollama — vérifie la connexion
        info("Connexion à Ollama...")
        if not ollama_actif():
            err("Ollama ne répond pas. Lance : ollama serve")
            raise SystemExit(1)
        ok("Ollama actif")
        cle_api = None

    # ── Choix modèle ─────────────────────────────────────────
    modeles = _lister_modeles(provider_cle, config.get("cles", {}).get(provider_cle))
    modele  = _choisir_modele(provider_cle, modeles, config)

    # Sauvegarde dernier provider/modèle utilisé
    config["dernier_provider"] = provider_cle
    config["dernier_modele"]   = modele
    sauvegarder_config(config)

    _provider_actif = provider_cle
    _modele_actif   = modele

    return provider_cle, modele


def _lister_modeles(provider_cle, cle_api=None):
    """Retourne la liste des modèles pour un provider."""
    if provider_cle == "ollama":
        try:
            r = requests.get(OLLAMA_TAGS, timeout=5)
            modeles = [m["name"] for m in r.json().get("models", [])]
            return modeles if modeles else PROVIDERS["ollama"]["modeles_defaut"]
        except Exception:
            return PROVIDERS["ollama"]["modeles_defaut"]
    else:
        return PROVIDERS[provider_cle]["modeles"]


def _choisir_modele(provider_cle, modeles, config):
    """Affiche la liste des modèles et demande le choix."""
    provider    = PROVIDERS[provider_cle]
    defaut_conf = config.get("dernier_modele") if config.get("dernier_provider") == provider_cle else None
    defaut      = defaut_conf or (modeles[0] if modeles else "")

    console.print(f"\n[bold cyan]Modèles {provider['nom']} :[/bold cyan]")
    for i, m in enumerate(modeles, 1):
        tag = ""
        if any(x in m.lower() for x in ["70b", "pro", "opus", "turbo", "coder", "reasoner"]):
            tag = "  [yellow]★ puissant[/yellow]"
        elif any(x in m.lower() for x in ["mini", "flash", "lite", "instant", "haiku", "1.5b", "0.5b", "1b"]):
            tag = "  [green]⚡ rapide[/green]"
        marker = " [dim](dernier utilisé)[/dim]" if m == defaut_conf else ""
        console.print(f"  [bold]{i}[/bold]. {m}{tag}{marker}")

    console.print()
    idx_defaut = (modeles.index(defaut) + 1) if defaut in modeles else 1
    choix = console.input(f"[cyan]Choix [{idx_defaut}] : [/cyan]").strip() or str(idx_defaut)

    if choix.isdigit():
        idx    = int(choix) - 1
        modele = modeles[idx] if 0 <= idx < len(modeles) else modeles[0]
    else:
        modele = next((m for m in modeles if choix.lower() in m.lower()), modeles[0])

    ok(f"Modèle : [bold]{modele}[/bold]")
    return modele


# ============================================================
#  COMPATIBILITE — anciennes fonctions conservées
# ============================================================
def choisir_modele():
    """Alias pour compatibilité — redirige vers le nouveau flow."""
    _, modele = choisir_provider_et_modele()
    return modele


def ollama_actif():
    try:
        requests.get(OLLAMA_TAGS, timeout=3)
        return True
    except Exception:
        return False


def lister_modeles():
    return _lister_modeles("ollama")


# ============================================================
#  ENVOI DES MESSAGES — routeur principal
# ============================================================
def demander(messages, modele, stream=True, timeout=300):
    """Point d'entrée universel — route vers le bon provider."""
    config      = charger_config()
    provider_id = config.get("dernier_provider", "ollama")
    cle_api     = config.get("cles", {}).get(provider_id)

    if provider_id == "ollama":
        return _demander_ollama(messages, modele, stream, timeout)
    elif provider_id == "claude":
        return _demander_claude(messages, modele, cle_api, stream, timeout)
    else:
        return _demander_openai_compat(messages, modele, cle_api, provider_id, stream, timeout)


def demander_conversation(messages, modele):
    return demander(messages, modele, stream=True, timeout=300)


# ============================================================
#  OLLAMA
# ============================================================
def _demander_ollama(messages, modele, stream=True, timeout=300):
    payload = {
        "model":    modele,
        "messages": messages,
        "stream":   stream,
        "options":  {"temperature": 0.2, "num_predict": 4096, "num_ctx": 8192}
    }
    try:
        if stream:
            return _stream_ollama(payload, timeout)
        r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        return r.json().get("message", {}).get("content", "")
    except requests.exceptions.ConnectionError:
        err("Ollama ne répond pas.")
        return None
    except requests.exceptions.Timeout:
        err(f"Timeout {timeout}s.")
        return None
    except Exception as e:
        err(f"Erreur Ollama : {e}")
        return None


def _stream_ollama(payload, timeout=300):
    reponse = ""
    affiche = False
    en_code = False
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=timeout) as r:
            for ligne in r.iter_lines():
                if not ligne:
                    continue
                try:
                    data  = json.loads(ligne)
                    token = data.get("message", {}).get("content", "")
                    reponse += token
                    if "```" in reponse[-20:]:
                        en_code = not en_code
                    if not en_code and "```" not in token:
                        if not affiche:
                            console.print("\n[bold cyan]Rolax >[/bold cyan] ", end="")
                            affiche = True
                        print(token, end="", flush=True)
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
        if affiche:
            print()
    except Exception as e:
        print()
        err(f"Stream Ollama : {e}")
    return reponse or None


# ============================================================
#  OPENAI-COMPATIBLE (Groq, Gemini, DeepSeek, OpenAI)
# ============================================================
def _demander_openai_compat(messages, modele, cle_api, provider_id, stream=True, timeout=300):
    url     = PROVIDERS[provider_id]["url"]
    headers = {
        "Authorization": f"Bearer {cle_api}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       modele,
        "messages":    messages,
        "stream":      stream,
        "temperature": 0.2,
        "max_tokens":  4096,
    }
    try:
        if stream:
            return _stream_openai(url, headers, payload, timeout)
        r   = requests.post(url, headers=headers, json=payload, timeout=timeout)
        rep = r.json()
        if "error" in rep:
            err(f"{PROVIDERS[provider_id]['nom']} : {rep['error'].get('message', rep['error'])}")
            return None
        return rep["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        err(f"Timeout {timeout}s.")
        return None
    except Exception as e:
        err(f"Erreur {provider_id} : {e}")
        return None


def _stream_openai(url, headers, payload, timeout=300):
    reponse = ""
    affiche = False
    en_code = False
    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout) as r:
            for ligne in r.iter_lines():
                if not ligne:
                    continue
                ligne = ligne.decode("utf-8") if isinstance(ligne, bytes) else ligne
                if ligne.startswith("data: "):
                    data_str = ligne[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data  = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        token = delta.get("content", "")
                        if not token:
                            continue
                        reponse += token
                        if "```" in reponse[-20:]:
                            en_code = not en_code
                        if not en_code and "```" not in token:
                            if not affiche:
                                console.print("\n[bold cyan]Rolax >[/bold cyan] ", end="")
                                affiche = True
                            print(token, end="", flush=True)
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        if affiche:
            print()
    except Exception as e:
        print()
        err(f"Stream : {e}")
    return reponse or None


# ============================================================
#  CLAUDE (Anthropic — format différent)
# ============================================================
def _demander_claude(messages, modele, cle_api, stream=True, timeout=300):
    url     = PROVIDERS["claude"]["url"]
    headers = {
        "x-api-key":         cle_api,
        "anthropic-version": "2023-06-01",
        "Content-Type":      "application/json",
    }
    # Claude sépare system des messages
    system_content = ""
    msgs_filtres   = []
    for m in messages:
        if m["role"] == "system":
            system_content = m["content"]
        else:
            msgs_filtres.append(m)

    payload = {
        "model":      modele,
        "max_tokens": 4096,
        "messages":   msgs_filtres,
        "stream":     stream,
    }
    if system_content:
        payload["system"] = system_content

    try:
        if stream:
            return _stream_claude(url, headers, payload, timeout)
        r   = requests.post(url, headers=headers, json=payload, timeout=timeout)
        rep = r.json()
        if "error" in rep:
            err(f"Claude : {rep['error'].get('message', rep['error'])}")
            return None
        return rep["content"][0]["text"]
    except requests.exceptions.Timeout:
        err(f"Timeout {timeout}s.")
        return None
    except Exception as e:
        err(f"Erreur Claude : {e}")
        return None


def _stream_claude(url, headers, payload, timeout=300):
    reponse = ""
    affiche = False
    en_code = False
    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout) as r:
            for ligne in r.iter_lines():
                if not ligne:
                    continue
                ligne = ligne.decode("utf-8") if isinstance(ligne, bytes) else ligne
                if ligne.startswith("data: "):
                    data_str = ligne[6:].strip()
                    if data_str in ("[DONE]", ""):
                        continue
                    try:
                        data = json.loads(data_str)
                        # Claude SSE : content_block_delta
                        if data.get("type") == "content_block_delta":
                            token = data.get("delta", {}).get("text", "")
                        elif data.get("type") == "message_delta":
                            break
                        else:
                            continue
                        if not token:
                            continue
                        reponse += token
                        if "```" in reponse[-20:]:
                            en_code = not en_code
                        if not en_code and "```" not in token:
                            if not affiche:
                                console.print("\n[bold cyan]Rolax >[/bold cyan] ", end="")
                                affiche = True
                            print(token, end="", flush=True)
                    except (json.JSONDecodeError, KeyError):
                        continue
        if affiche:
            print()
    except Exception as e:
        print()
        err(f"Stream Claude : {e}")
    return reponse or None
