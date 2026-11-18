"""Logique commune des vues : saisie des paramètres, exécution, affichage, menu post-exécution.

Chaque vue de catégorie (hardware, communication, system, media) délègue ici.
Les vues retournent "back" (retour au menu) ou "quit" (quitter l'application).
"""
from __future__ import annotations

import re
import shlex
from typing import Any, Callable, Dict, List, Optional, Union

from rich.text import Text

import catalog
import config
import runner
import ui

# Hooks de rendu enrichi : {commande: fonction(result, args)} (jauges, liens…)
Hook = Callable[[Dict[str, Any], List[str]], None]
HOOKS: Dict[str, Hook] = {}


def register_hook(cmd_name: str) -> Callable[[Hook], Hook]:
    """Décorateur : associe un rendu enrichi à une commande."""
    def decorator(fn: Hook) -> Hook:
        HOOKS[cmd_name] = fn
        return fn
    return decorator


# ── Saisie des arguments ─────────────────────────────────────────────────────
def _should_ask(arg: Dict[str, Any], values: Dict[str, Any]) -> bool:
    """Évalue les conditions `when` / `when_set` d'un argument."""
    for key, expected in arg.get("when", {}).items():
        current = values.get(key)
        if isinstance(expected, (list, tuple, set)):
            if current not in expected:
                return False
        elif current != expected:
            return False
    dep = arg.get("when_set")
    return not (dep and not values.get(dep))


def _validate(arg: Dict[str, Any], value: str) -> Optional[str]:
    """Retourne un message d'erreur si la valeur est invalide, sinon None."""
    if value == "":
        return "Ce champ est obligatoire." if arg.get("required") else None
    kind = arg.get("type", "text")
    if kind == "int" and not re.fullmatch(r"-?\d+", value):
        return "Entre un nombre entier."
    if kind == "number":
        try:
            float(value)
        except ValueError:
            return "Entre un nombre (ex : 1.0)."
    return None


def _ask_value(arg: Dict[str, Any]) -> Any:
    """Pose la question correspondant à un argument (selon son type)."""
    kind, prompt, default = arg.get("type", "text"), arg["prompt"], arg.get("default")
    if kind == "bool":
        return ui.confirm(prompt, default=bool(default))
    while True:
        if kind == "choice":
            value = ui.ask(prompt, default=default, choices=arg.get("choices"))
        elif arg.get("secret"):
            value = ui.ask_secret(prompt)
        else:
            value = ui.ask(prompt, default=default)
        error = _validate(arg, value)
        if error is None:
            return value
        ui.console.print(Text(f"  ✗ {error}", style="error"))


def collect_args(name: str) -> List[str]:
    """Demande les arguments décrits dans le catalogue et retourne la liste argv."""
    entry = catalog.get(name)
    if not entry or not entry["args"]:
        return []
    ui.console.print(Text("Paramètres — Entrée = valeur par défaut · Ctrl+C = annuler",
                          style="muted"))
    values: Dict[str, Any] = {}
    for arg in entry["args"]:
        if _should_ask(arg, values):
            values[arg["name"]] = _ask_value(arg)
    return catalog.build_args(name, values)


# ── Exécution et affichage ───────────────────────────────────────────────────
def execute(name: str, args: List[str]) -> Dict[str, Any]:
    """Lance la commande avec un spinner et retourne le résultat."""
    entry = catalog.get(name) or {}
    hint = entry.get("hint") or "Exécution en cours…"
    ui.print_command_line(shlex.join([config.EXEC_ALIASES.get(name, name)] + runner.expand_args(args)))
    with ui.with_spinner(f"{name} — {hint}"):
        return runner.run_command(name, args, timeout=entry.get("timeout"))


def _run_hook(name: str, result: Dict[str, Any], args: List[str]) -> None:
    """Exécute le rendu enrichi d'une commande, sans jamais planter l'UI."""
    hook = HOOKS.get(name)
    if not hook or not result.get("ok"):
        return
    try:
        hook(result, args)
    except Exception as exc:  # noqa: BLE001 - le rendu enrichi est optionnel
        ui.print_warning(f"Rendu enrichi indisponible : {exc}")


def _toggle_favorite(name: str) -> None:
    """Ajoute ou retire la commande des favoris."""
    if config.is_favorite(name):
        done = config.remove_favorite(name)
        msg = f"{name} retiré des favoris."
    else:
        done = config.add_favorite(name)
        msg = f"{name} ajouté aux favoris ★"
    if done:
        ui.print_success(msg)
    else:
        ui.print_error("Impossible d'écrire ~/.termux-studio/favorites.json")


def _post_menu(name: str, entry: Dict[str, Any], result: Dict[str, Any], as_json: bool) -> str:
    """Menu « relancer / modifier / vue / favori / retour / quitter » → nom d'action."""
    actions = {"1": "retry", "4": "fav", "0": "back", "q": "quit"}
    items = [("1", "↻ Relancer", "Mêmes paramètres")]
    if entry["args"]:
        items.append(("2", "✎ Modifier les paramètres", "Ressaisir puis relancer"))
        actions["2"] = "edit"
    if ui.is_table_data(result.get("data")):
        items.append(("3", "{ } Vue Table" if as_json else "{ } Vue JSON", "Basculer l'affichage"))
        actions["3"] = "json"
    fav = config.is_favorite(name)
    items.append(("4", "☆ Retirer des favoris" if fav else "★ Ajouter aux favoris", ""))
    items += [("0", "← Retour", ""), ("q", "✗ Quitter", "")]
    ui.print_menu("Et maintenant ?", items)
    return actions[ui.choose(actions.keys(), default="0")]


def _show_loop(name: str, entry: Dict[str, Any], args: List[str], result: Dict[str, Any]) -> str:
    """Affiche le résultat puis le menu post-exécution ; retourne l'action choisie."""
    as_json, first = False, True
    while True:
        if not first:
            ui.clear()
        first = False
        ui.print_result(result, title=name, as_json=as_json)
        _run_hook(name, result, args)
        if not result.get("ok") and entry.get("permission"):
            ui.print_warning(f"Vérifie la permission Android « {entry['permission']} » "
                             "accordée à Termux:API.")
        action = _post_menu(name, entry, result, as_json)
        if action == "json":
            as_json = not as_json
        elif action == "fav":
            _toggle_favorite(name)
        else:
            return action


def command_session(name: str) -> str:
    """Parcours complet d'une commande : saisie → exécution → résultat → actions."""
    entry = catalog.get(name)
    if entry is None:
        ui.print_error(f"Commande inconnue : {name}")
        return "back"
    ui.clear()
    ui.print_command_card(name, entry)
    try:
        args = collect_args(name)
        while True:
            if entry.get("confirm") and not ui.confirm(entry["confirm"], default=False):
                ui.print_warning("Annulé.")
                return "back"
            result = execute(name, args)
            action = _show_loop(name, entry, args, result)
            if action == "edit":
                args = collect_args(name)
            elif action != "retry":
                return action
    except KeyboardInterrupt:
        ui.console.print()
        ui.print_warning("Interrompu — retour à la liste.")
        return "back"


# ── Listes de commandes ──────────────────────────────────────────────────────
NamesSource = Union[List[str], Callable[[], List[str]]]


def _command_items(names: List[str]) -> List[Any]:
    """Items de menu (clé, libellé, description) pour une liste de commandes."""
    items: List[Any] = []
    for i, name in enumerate(names, 1):
        star = "★ " if config.is_favorite(name) else ""
        desc = (catalog.get(name) or {}).get("description", "")
        items.append((str(i), star + name.replace("termux-", "", 1), desc))
    return items + [None, ("0", "← Retour", ""), ("q", "✗ Quitter", "")]


def run_command_list(title: str, source: NamesSource, subtitle: Optional[str] = None) -> str:
    """Menu générique d'une liste de commandes. Retourne "back" ou "quit"."""
    while True:
        names = source() if callable(source) else source
        if not names:
            ui.print_warning("Aucune commande à afficher.")
            return "back"
        ui.clear()
        ui.print_menu(title, _command_items(names), subtitle)
        valid = [str(i) for i in range(1, len(names) + 1)] + ["0", "q"]
        try:
            choice = ui.choose(valid)
        except KeyboardInterrupt:
            return "back"
        if choice == "0":
            return "back"
        if choice == "q":
            return "quit"
        if command_session(names[int(choice) - 1]) == "quit":
            return "quit"


def run_category(category: str) -> str:
    """Menu d'une catégorie du catalogue. Retourne "back" ou "quit"."""
    meta = catalog.CATEGORIES[category]
    names = list(catalog.get_by_category(category))
    return run_command_list(f"{meta['icon']}  {meta['title']}", names,
                            subtitle=f"{len(names)} commandes · {meta['description']}")
