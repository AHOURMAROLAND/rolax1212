# rolax1212 v1.0

Agent de développement local — style Claude Code, powered by Ollama.

Créé par **Roland**.

---

## Installation

```bash
pip install rolax1212
```

> **Prérequis** : [Ollama](https://ollama.com) doit être installé et lancé avec au moins un modèle.
>
> ```bash
> ollama pull qwen2.5:1.5b
> ```

---

## Utilisation

```bash
# Dans le dossier de ton projet
rolax1212

# Ou avec un chemin direct
rolax1212 C:\Users\rolan\MonProjet
```

---

## Commandes disponibles

| Commande | Description |
|---|---|
| `plan [texte libre]` | Décris ton projet → génère Task.md automatiquement |
| `task` | Exécute toutes les tâches du Task.md |
| `audit` | Rapport C/U/F (bugs, améliorations, suggestions) |
| `structure` | Affiche l'arborescence du projet |
| `lis [fichier]` | Affiche un fichier avec coloration syntaxique |
| `exec [fichier]` | Exécute un fichier (Python, PHP, JS, Bash) |
| `aide` | Affiche l'aide |
| `exit` | Quitte rolax1212 |

---

## Fonctionnalités

### Task.md en langage libre
Écris ce que tu veux faire en français naturel :
```
plan je veux un site pour gérer les élèves
faut un login pour le directeur
les profs voient leurs classes
export PDF des bulletins
```
rolax1212 génère un `Task.md` structuré, te le montre et demande validation.

### Rapport C/U/F automatique
Au démarrage sur un projet existant, rolax1212 analyse tout et affiche :
- **[C] CHECK** — Bugs détectés et corrigés automatiquement
- **[U] UPDATE** — Améliorations à faire maintenant
- **[F] FUTURE** — Fonctionnalités à ajouter plus tard

### Génération de code multi-langages
```
crée un UserController.php avec login et register
génère une classe Java User avec getters et setters
implémente une API REST avec Flask
```
Le code est vérifié automatiquement après génération.

---

## Modèles recommandés

| Modèle | Usage |
|---|---|
| `qwen2.5:1.5b` | Conversation, questions rapides |
| `qwen2.5:7b` | Code de qualité |
| `gpt-oss:120b-cloud` | PHP/Java complexe, Laravel |

---

## Langages supportés

PHP, Python, Java, JavaScript, TypeScript, HTML, CSS, SQL, Bash, C, C++

---

## License

MIT — Libre d'utilisation et de modification.
