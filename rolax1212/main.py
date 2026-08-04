# ============================================================
#  main.py — Point d'entrée
#  rolax1212 v4.0.0 by Roland
# ============================================================

import sys
from pathlib import Path
from .ui     import console, banniere, separateur
from .llm    import choisir_provider_et_modele
from .config import setup_initial
from .agent  import lancer


def main():
    banniere()
    separateur()

    # Premier lancement → assistant configuration variables système
    setup_initial()

    try:
        provider, modele = choisir_provider_et_modele()
    except SystemExit:
        sys.exit(1)

    separateur()

    if len(sys.argv) > 1:
        path_projet = " ".join(sys.argv[1:])
    else:
        path_projet = console.input(
            f"\n[cyan]Chemin du projet[/cyan] [dim](Entrée = dossier actuel)[/dim] : "
        ).strip() or str(Path.cwd())

    separateur()
    lancer(modele, path_projet)


if __name__ == "__main__":
    main()
