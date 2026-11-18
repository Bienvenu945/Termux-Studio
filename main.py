#!/usr/bin/env python3
"""Termux API Studio — point d'entrée.

Exemples :
    python main.py                       # TUI complet
    python main.py --check               # vérifie l'environnement
    python main.py --demo                # TUI avec données fictives
    python main.py --category hardware   # ouvre directement une catégorie
    python main.py --demo --run termux-sms-list -l 5
    python main.py --fav add termux-torch
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys
import traceback
from typing import List, Optional

import catalog
import config

THEME_CHOICES = ["cyan", "magenta", "mono"]


def build_parser() -> argparse.ArgumentParser:
    """Construit le parseur d'arguments."""
    p = argparse.ArgumentParser(
        prog="main.py", description=f"{config.APP_NAME} — {config.APP_TAGLINE}",
        epilog="Astuce : place --demo / --theme AVANT --run (tout ce qui suit --run est transmis à la commande).")
    p.add_argument("--version", action="store_true", help="affiche la version")
    p.add_argument("--check", action="store_true", help="vérifie l'environnement termux-api")
    p.add_argument("--demo", action="store_true", help="mode démo : données fictives, rien n'est exécuté")
    p.add_argument("--theme", choices=THEME_CHOICES, help="palette : cyan | magenta | mono")
    p.add_argument("--category", choices=list(catalog.CATEGORIES), help="lance directement une catégorie")
    p.add_argument("--fav", nargs="+", metavar="ARG",
                   help="favoris : 'add <cmd>' | 'remove <cmd>' | 'list'")
    p.add_argument("--run", nargs=argparse.REMAINDER, metavar="CMD",
                   help="mode CLI direct : --run <cmd> [args...]")
    return p


def _load_ui():
    """Importe ui (donc Rich) ; retourne None avec un message clair si Rich manque."""
    try:
        import ui
        return ui
    except ImportError as exc:
        print(f"Rich est requis ({exc}). Installe-le :  pip install -r requirements.txt",
              file=sys.stderr)
        return None


def _cmd_version() -> int:
    """--version : fonctionne même sans Rich."""
    line = f"{config.APP_NAME} v{config.APP_VERSION}"
    try:
        import ui
        from rich.text import Text
        ui.console.print(Text.assemble((config.APP_NAME, "title"), (f" v{config.APP_VERSION}", "accent")))
    except ImportError:
        print(line)
    return 0


def _cmd_check(ui) -> int:
    """--check : rapport d'environnement (code 0 même hors Termux)."""
    ui.print_header(compact=True)
    ui.print_env_report(config.check_environment())
    return 0


def _cmd_run(ui, tokens: List[str]) -> int:
    """--run <cmd> [args...] : exécution directe puis affichage Rich."""
    import runner
    if not tokens:
        ui.print_error("--run attend un nom de commande, ex : --run termux-battery-status")
        return 2
    name = catalog.normalize_name(tokens[0])
    entry = catalog.get(name)
    with ui.with_spinner(f"Exécution de {name}…"):
        result = runner.run_command(name, tokens[1:], timeout=entry["timeout"] if entry else None)
    ui.print_result(result, title=name)
    return 0 if result["ok"] else 1


def _fav_list(ui) -> int:
    favs = config.load_favorites()
    if not favs:
        ui.print_warning("Aucun favori. Ajoute-en : python main.py --fav add termux-torch")
        return 0
    rows = {f: (catalog.get(f) or {}).get("description", "(commande hors catalogue)") for f in favs}
    ui.print_kv_table(rows, f"★ Favoris ({len(favs)})")
    ui.print_rule()
    return 0


def _cmd_fav(ui, tokens: List[str]) -> int:
    """--fav add|remove <cmd> | list."""
    action = tokens[0].lower()
    if action == "list":
        return _fav_list(ui)
    if action not in ("add", "remove") or len(tokens) < 2:
        ui.print_error("Usage : --fav add <cmd> | --fav remove <cmd> | --fav list")
        return 2
    name = catalog.normalize_name(tokens[1])
    if action == "add":
        if catalog.get(name) is None:
            ui.print_error(f"Commande inconnue : {name}")
            return 1
        added = config.add_favorite(name)
        (ui.print_success if added else ui.print_warning)(
            f"{name} ajouté aux favoris ★" if added else f"{name} est déjà en favori (ou écriture impossible).")
        return 0 if added else 1
    removed = config.remove_favorite(name)
    (ui.print_success if removed else ui.print_warning)(
        f"{name} retiré des favoris." if removed else f"{name} n'était pas en favori.")
    return 0 if removed else 1


def _cmd_category(ui, name: str) -> int:
    """--category <nom> : ouvre directement la vue."""
    module = importlib.import_module(f"views.{name}")
    module.run()
    return 0


def _startup_alert(ui) -> None:
    """Alerte au démarrage si termux-api manque ; propose le mode démo hors Termux."""
    env = config.check_environment()
    if env["ok"] or config.is_demo():
        return
    ui.print_env_alert(env)
    if sys.stdin.isatty():
        try:
            if ui.confirm("Activer le mode démo (données fictives) ?", default=not env["termux"]):
                config.set_demo(True)
        except KeyboardInterrupt:
            pass


def _cmd_tui(ui) -> int:
    """TUI complet."""
    from views import menu
    _startup_alert(ui)
    return menu.run()


def _dispatch(ui, args: argparse.Namespace) -> int:
    """Choisit le mode à lancer selon les arguments."""
    if args.check:
        return _cmd_check(ui)
    if args.fav:
        return _cmd_fav(ui, args.fav)
    if args.run is not None:
        return _cmd_run(ui, args.run)
    if args.category:
        return _cmd_category(ui, args.category)
    return _cmd_tui(ui)


def _silence_broken_pipe() -> None:
    """Sortie fermée par le lecteur (ex. `| head`) : on quitte sans traceback."""
    try:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    except (OSError, ValueError):
        pass


def main(argv: Optional[List[str]] = None) -> int:
    """Point d'entrée : retourne le code de sortie."""
    args = build_parser().parse_args(argv)
    if args.version:
        return _cmd_version()
    config.ensure_dirs()
    if args.demo:
        config.set_demo(True)
    ui = _load_ui()
    if ui is None:
        return 2
    if args.theme:
        ui.apply_theme(args.theme)
    try:
        return _dispatch(ui, args)
    except BrokenPipeError:
        _silence_broken_pipe()
        return 0
    except KeyboardInterrupt:
        ui.console.print()
        return 130
    except Exception as exc:  # noqa: BLE001 - jamais de traceback brut pour l'utilisateur
        ui.print_error(f"Erreur inattendue : {exc}")
        if os.environ.get("TERMUX_STUDIO_DEBUG"):
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
