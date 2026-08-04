# rolax1212 v4.2.0

```
         ██████╗  ██████╗ ██╗      █████╗ ██╗  ██╗  ██╗██████╗  ██╗██████╗
  ██╗   ██╔══██╗██╔═══██╗██║     ██╔══██╗╚██╗██╔╝  ██║╚════██╗███║╚════██╗
 ██╔╝█  ██████╔╝██║   ██║██║     ███████║ ╚███╔╝   ██║ █████╔╝╚██║ █████╔╝
 ╚██╗   ██╔══██╗██║   ██║██║     ██╔══██║ ██╔██╗   ██║██╔═══╝  ██║██╔═══╝
  ╚═╝   ██║  ██║╚██████╔╝███████╗██║  ██║██╔╝ ██╗  ██║███████╗ ██║███████╗
         ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═╝╚══════╝ ╚═╝╚══════╝

  v4.2.0  •  by Roland  •  Powered by Ollama | Groq | Gemini | Claude | DeepSeek | OpenAI
```

Agent de développement local — style Claude Code.  
Décris ton projet en français, rolax1212 génère, vérifie et corrige le code automatiquement.

Créé par **Roland**.

---

## Installation

```bash
pip install rolax1212
```

> **Prérequis pour le mode local** : [Ollama](https://ollama.com) installé et lancé.
> ```bash
> ollama serve
> ollama pull qwen2.5:1.5b
> ```
>
> **Providers cloud** : Groq, Gemini, Claude, DeepSeek, OpenAI — clé API suffisante, aucune installation.

---

## Démarrage rapide

```bash
# Dans le dossier de ton projet
rolax1212

# Ou avec un chemin direct
rolax1212 C:\Users\rolan\MonProjet
```

Au **premier lancement**, rolax1212 propose de configurer tes clés API directement dans les variables d'environnement système — plus besoin de les ressaisir.

---

## Providers supportés

| Provider | Modèles recommandés | Clé API |
|---|---|---|
| 🦙 **Ollama** (local) | qwen2.5:7b, llama3:8b, mistral:7b | aucune |
| ⚡ **Groq** | llama-3.3-70b-versatile, mixtral-8x7b | `GROQ_API_KEY` |
| ✨ **Gemini** | gemini-2.0-flash, gemini-1.5-pro | `GEMINI_API_KEY` |
| 🧠 **Claude** | claude-sonnet-4-5, claude-opus-4-5 | `ANTHROPIC_API_KEY` |
| 🔍 **DeepSeek** | deepseek-chat, deepseek-coder | `DEEPSEEK_API_KEY` |
| 🤖 **OpenAI** | gpt-4o, gpt-4o-mini | `OPENAI_API_KEY` |

Les clés sont lues automatiquement depuis les **variables d'environnement système** — tu peux aussi les définir manuellement :

```bash
# Windows
setx GROQ_API_KEY "gsk_xxxxxxxxxxxx"

# Linux / macOS
export GROQ_API_KEY="gsk_xxxxxxxxxxxx"
```

---

## Commandes disponibles

| Commande | Description |
|---|---|
| `plan [texte libre]` | Décris ton projet → génère Task.md automatiquement |
| `task` | Exécute toutes les tâches du Task.md |
| `audit` | Rapport C/U/F (bugs, améliorations, suggestions) |
| `init [framework]` | Initialise un projet (Django, Laravel, React…) |
| `env` | Configurer les variables d'environnement du projet (.env) |
| `git` | Commit automatique avec message généré par IA |
| `git status` | Fichiers modifiés |
| `git log` | Derniers commits |
| `git push` | Push vers GitHub |
| `provider` | Changer de provider LLM en cours de session |
| `config` | Afficher la configuration et les clés API |
| `config setup` | Relancer l'assistant de configuration |
| `cle <provider> <valeur>` | Ajouter/modifier une clé API |
| `structure` | Affiche l'arborescence du projet |
| `lis [fichier]` | Affiche un fichier avec coloration syntaxique |
| `exec [fichier]` | Exécute un fichier (Python, PHP, JS, Bash) |
| `framework` | Changer de framework en cours de session |
| `aide` | Affiche l'aide complète |
| `exit` | Quitter |

---

## Fonctionnalités

### Génération de code intelligente
Décris ce que tu veux en langage naturel :
```
crée un UserController.php avec login et register
génère une classe Java User avec getters et setters
implémente une API REST avec Flask
```
Le code généré est **vérifié et corrigé automatiquement** (3 tentatives max avec feedback d'erreur au LLM).

### Task.md en langage libre
```
plan je veux un site pour gérer les élèves
faut un login pour le directeur
les profs voient leurs classes
export PDF des bulletins
```
rolax1212 génère un `Task.md` structuré, te le montre, demande validation puis exécute chaque tâche.

### Rapport C/U/F automatique
Au démarrage sur un projet existant, rolax1212 analyse tout le code et affiche :
- **[C] CHECK** — Bugs détectés et corrigés automatiquement
- **[U] UPDATE** — Améliorations à faire maintenant
- **[F] FUTURE** — Fonctionnalités à ajouter plus tard

### Git intelligent
```
git
```
Analyse les fichiers modifiés, génère un message de commit conventionnel (feat/fix/refactor…) via le LLM et confirme avant de committer.

### Détection de framework par IA
Rolax1212 analyse ton projet et identifie automatiquement le framework utilisé (Django, Laravel, React, etc.) pour adapter la génération de code.

### Reprise de session
Si le programme est interrompu pendant l'exécution d'un Task.md, il propose de reprendre exactement là où il s'est arrêté.

---

## Frameworks supportés

| Catégorie | Frameworks |
|---|---|
| Python | Django • FastAPI • Flask |
| PHP | Laravel • Symfony |
| Java | Spring Boot |
| JavaScript / TypeScript | Express.js • NestJS • React • Next.js • Vue.js • Angular |
| Mobile | React Native • Flutter |

---

## Langages supportés

PHP • Python • Java • JavaScript • TypeScript • HTML • CSS • SQL • Bash • C • C++ • Dart

---

## Historique des versions

| Version | Changements |
|---|---|
| **4.2.0** | Variables d'environnement système (SETX Windows / export Linux), setup initial, lecture auto `os.environ` |
| **4.1.0** | Gestion `.env` projet — détection variables manquantes par framework, configuration interactive |
| **4.0.0** | Multi-providers LLM — Groq, Gemini, Claude, DeepSeek, OpenAI, clés API persistantes |
| **3.0.0** | Header ASCII art, détection framework par IA, Ctrl+C avec confirmation |
| **2.0.6** | Détection framework par IA (LLM), Ctrl+C sécurisé |
| **2.0.5** | Première version publique PyPI |

---

## License

MIT — Libre d'utilisation et de modification.
