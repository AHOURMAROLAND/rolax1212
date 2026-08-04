# ============================================================
#  ui.py — Affichage terminal
#  rolax1212 v2.0.1 by Roland
# ============================================================

from rich.console  import Console
from rich.panel    import Panel
from rich.table    import Table
from rich.syntax   import Syntax
from rich.prompt   import Prompt, Confirm
from rich.markdown import Markdown

console = Console()

VERSION = "2.0.1"
AUTEUR  = "Roland"

# ── Couleurs ────────────────────────────────────────────────
def ok(t):    console.print(f"[bold green][OK][/bold green] {t}")
def info(t):  console.print(f"[cyan][>>][/cyan] {t}")
def warn(t):  console.print(f"[bold yellow][!][/bold yellow] {t}")
def err(t):   console.print(f"[bold red][ERR][/bold red] {t}")
def titre(t): console.print(f"\n[bold cyan]{t}[/bold cyan]")
def separateur(): console.print("[dim]" + "─" * 62 + "[/dim]")

def code(contenu, langage="text", lignes=True):
    console.print(Syntax(contenu, langage, theme="monokai", line_numbers=lignes))

def demander(question, defaut=None):
    return Prompt.ask(f"[cyan]{question}[/cyan]", default=defaut)

def confirmer(question, defaut=True):
    return Confirm.ask(f"[cyan]{question}[/cyan]", default=defaut)

# ── Bannières ───────────────────────────────────────────────
def banniere():
    console.print(Panel(
        f"[bold cyan]ROLAX1212[/bold cyan]  —  Agent de développement local\n"
        f"[dim]Version {VERSION}  •  by {AUTEUR}  •  Powered by Ollama[/dim]",
        title="[bold cyan][ ROLAX1212 ][/bold cyan]",
        style="cyan"
    ))

def banniere_session(modele, path_projet):
    console.print(Panel(
        f"[bold cyan]ROLAX1212[/bold cyan]  —  Agent de développement local\n"
        f"[dim]Modèle  :[/dim] [yellow]{modele}[/yellow]\n"
        f"[dim]Projet  :[/dim] [white]{path_projet}[/white]\n"
        f"[dim]Commandes :[/dim] "
        f"[cyan]plan[/cyan] • [cyan]task[/cyan] • [cyan]audit[/cyan] • "
        f"[cyan]init[/cyan] • [cyan]git[/cyan] • [cyan]structure[/cyan] • "
        f"[cyan]aide[/cyan] • [cyan]exit[/cyan]",
        title="[bold cyan][ ROLAX1212 v2.0.1 ][/bold cyan]",
        style="cyan"
    ))

# ── Aide ────────────────────────────────────────────────────
def afficher_aide():
    console.print(Markdown("""
## Commandes disponibles

| Commande | Description |
|---|---|
| `plan [texte libre]` | Décris ton projet → génère Task.md |
| `task` | Exécute les tâches du Task.md |
| `audit` | Rapport C/U/F (bugs, améliorations, suggestions) |
| `init [framework]` | Initialise un projet avec le bon framework |
| `git` | Commit automatique intelligent |
| `git status` | Fichiers modifiés |
| `git log` | Derniers commits |
| `git push` | Push vers GitHub |
| `structure` | Arborescence du projet |
| `lis [fichier]` | Affiche un fichier |
| `exec [fichier]` | Exécute un fichier |
| `framework` | Changer de framework |
| `aide` | Cette aide |
| `exit` | Quitter |

## Frameworks supportés
Django • FastAPI • Flask • Laravel • Symfony • Spring Boot
Express.js • NestJS • React • Next.js • Vue.js • Angular
React Native • Flutter

## Exemples
```
plan je veux un site de gestion d'élèves avec Django
init django
crée un UserController.php avec login et register
git
```
"""))

# ── Audit C/U/F ─────────────────────────────────────────────
def afficher_audit(rapport):
    checks  = rapport.get("check",  [])
    updates = rapport.get("update", [])
    futures = rapport.get("future", [])

    console.print()
    console.print(Panel(
        f"[bold green][C] CHECK[/bold green]  {len(checks)} bug(s)  •  "
        f"[bold yellow][U] UPDATE[/bold yellow]  {len(updates)} amélioration(s)  •  "
        f"[bold cyan][F] FUTURE[/bold cyan]  {len(futures)} suggestion(s)",
        title="[bold white]AUDIT DU PROJET[/bold white]",
        style="white"
    ))

    if checks:
        console.print(f"\n[bold green][ C ] CHECK[/bold green]")
        separateur()
        for item in checks:
            statut = "[green]corrigé[/green]" if item.get("corrige") else "[red]manuel requis[/red]"
            console.print(f"  [white]{item.get('fichier','?')}[/white]  [dim]{item.get('probleme','?')}[/dim]  → {statut}")
    else:
        console.print(f"\n[bold green][ C ] CHECK[/bold green] — [green]Aucun bug détecté[/green]")

    console.print(f"\n[bold yellow][ U ] UPDATE[/bold yellow]")
    separateur()
    for u in updates or ["Aucune amélioration suggérée."]:
        console.print(f"  [yellow]•[/yellow] {u}")

    console.print(f"\n[bold cyan][ F ] FUTURE[/bold cyan]")
    separateur()
    for f in futures or ["Aucune suggestion."]:
        console.print(f"  [cyan]→[/cyan] {f}")
    console.print()

# ── Résultats ────────────────────────────────────────────────
def projet_termine(fichiers_crees):
    console.print(Panel(
        "[bold green]PROJET TERMINÉ[/bold green]\n"
        + "\n".join(f"  [green]✓[/green] {f}" for f in fichiers_crees),
        title="[bold green][ OK ][/bold green]", style="green"
    ))

def projet_termine_avertissement(fichiers_crees):
    console.print(Panel(
        "[bold yellow]TERMINÉ AVEC AVERTISSEMENTS[/bold yellow]\n"
        + "\n".join(f"  [yellow]•[/yellow] {f}" for f in fichiers_crees)
        + "\n[dim]Vérification manuelle recommandée.[/dim]",
        title="[bold yellow][ ! ][/bold yellow]", style="yellow"
    ))
