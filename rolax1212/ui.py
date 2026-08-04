# ============================================================
#  ui.py — Affichage terminal
#  rolax1212 v2.0.6 by Roland
# ============================================================

from rich.console  import Console
from rich.panel    import Panel
from rich.table    import Table
from rich.syntax   import Syntax
from rich.prompt   import Prompt, Confirm
from rich.markdown import Markdown
from rich.text     import Text

console = Console()

VERSION = "4.0.0"
AUTEUR  = "Roland"

# ── ASCII Art — ROLAX1212 style pixel bloc ───────────────────
# Lignes du logo : partie gauche (ROLAX) en bleu, droite (1212) en cyan
_LOGO = [
    (" ██████╗  ██████╗ ██╗      █████╗ ██╗  ██╗",  "  ██╗██████╗  ██╗██████╗ "),
    (" ██╔══██╗██╔═══██╗██║     ██╔══██╗╚██╗██╔╝",  "  ██║╚════██╗███║╚════██╗"),
    (" ██████╔╝██║   ██║██║     ███████║ ╚███╔╝ ",  "  ██║ █████╔╝╚██║ █████╔╝"),
    (" ██╔══██╗██║   ██║██║     ██╔══██║ ██╔██╗ ",  "  ██║██╔═══╝  ██║██╔═══╝ "),
    (" ██║  ██║╚██████╔╝███████╗██║  ██║██╔╝ ██╗",  "  ██║███████╗ ██║███████╗"),
    (" ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝", "  ╚═╝╚══════╝ ╚═╝╚══════╝"),
]

# Chevron style image : > en dégradé bleu→magenta
_CHEVRON = [
    ("  ██╗  ",  "blue"),
    (" ██╔╝  ",  "blue"),
    (" ╚██╗  ",  "magenta"),
    ("  ╚═╝  ",  "blue"),
]


def _print_banniere_ascii():
    """Affiche le header ASCII art style image (chevron + ROLAX1212)."""
    console.print()

    # On aligne chevron (4 lignes) avec logo (6 lignes) — padding haut de 1
    chevron_pad = 1  # décalage vertical pour centrer le chevron (4 lignes) sur 6

    for i, (left, right) in enumerate(_LOGO):
        t = Text()

        # Chevron sur lignes 1-4 (index 1 à 4)
        chev_idx = i - chevron_pad
        if 0 <= chev_idx < len(_CHEVRON):
            chev_txt, chev_color = _CHEVRON[chev_idx]
            t.append(chev_txt, style=f"bold {chev_color}")
        else:
            t.append("        ")  # 8 espaces de padding

        # ROLAX en bleu, 1212 en cyan
        t.append(left,  style="bold blue")
        t.append(right, style="bold cyan")
        console.print(t)

    console.print()


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
    _print_banniere_ascii()
    console.print(
        f"  [dim]v{VERSION}  •  by {AUTEUR}  •  Powered by Ollama  •  "
        f"[cyan]plan[/cyan] [dim]|[/dim] [cyan]task[/cyan] [dim]|[/dim] "
        f"[cyan]audit[/cyan] [dim]|[/dim] [cyan]git[/cyan] [dim]|[/dim] "
        f"[cyan]aide[/cyan][/dim]"
    )
    console.print()

def banniere_session(modele, path_projet):
    _print_banniere_ascii()
    console.print(Panel(
        f"[dim]Modèle  :[/dim] [yellow]{modele}[/yellow]\n"
        f"[dim]Projet  :[/dim] [white]{path_projet}[/white]\n"
        f"[dim]Commandes :[/dim] "
        f"[cyan]plan[/cyan] • [cyan]task[/cyan] • [cyan]audit[/cyan] • "
        f"[cyan]init[/cyan] • [cyan]git[/cyan] • [cyan]structure[/cyan] • "
        f"[cyan]aide[/cyan] • [cyan]exit[/cyan]",
        title=f"[bold cyan][ ROLAX1212 v{VERSION} ][/bold cyan]",
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
| `provider` | Changer de provider LLM (Ollama/Groq/Gemini…) |
| `config` | Afficher la configuration et les clés API |
| `cle <provider> <valeur>` | Sauvegarder une clé API |
| `cle <provider> supprimer` | Supprimer une clé API |
| `aide` | Cette aide |
| `exit` | Quitter |

## Providers supportés
Ollama (local) • Groq • Gemini • Claude • DeepSeek • OpenAI

## Frameworks supportés
Django • FastAPI • Flask • Laravel • Symfony • Spring Boot
Express.js • NestJS • React • Next.js • Vue.js • Angular
React Native • Flutter

## Exemples
```
plan je veux un site de gestion d'élèves avec Django
init django
crée un UserController.php avec login et register
provider
cle groq gsk_xxxxxxxxxxxx
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
