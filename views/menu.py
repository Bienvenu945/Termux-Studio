"""Menu principal : catégories, favoris, recherche, infos, boucle principale (Ctrl+C géré)."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

import catalog
import config
import ui

from . import communication, hardware, media, run_command_list, system

# Clé de catégorie → module de vue (chacun expose run())
CATEGORY_VIEWS = {
    "hardware": hardware,
    "communication": communication,
    "system": system,
    "media": media,
}

Action = Tuple[str, Callable[[], Optional[str]]]


def _pause() -> None:
    """Attend Entrée (Ctrl+C accepté : on revient simplement au menu)."""
    try:
        ui.ask("Entrée pour continuer", default="")
    except KeyboardInterrupt:
        pass


def _show_infos() -> Optional[str]:
    """Écran Infos : état de l'environnement, version, chemins."""
    ui.clear()
    ui.print_rule("ℹ  Infos")
    ui.print_env_report(config.check_environment())
    _pause()
    return None


def _show_favorites() -> Optional[str]:
    """Écran Favoris (relu à chaque tour : les ajouts/retraits sont visibles)."""
    def names() -> List[str]:
        return [n for n in config.load_favorites() if catalog.get(n)]

    if not names():
        ui.print_warning("Aucun favori. Ajoute-en depuis une commande (★) "
                         "ou : python main.py --fav add termux-torch")
        _pause()
        return None
    return run_command_list("★  Favoris", names)


def _show_search() -> Optional[str]:
    """Recherche par mot-clé dans les noms et descriptions."""
    ui.clear()
    ui.print_rule("🔎 Recherche")
    query = ui.ask("Mot-clé (nom, catégorie ou description)")
    if not query:
        return None
    found = catalog.search(query)
    if not found:
        ui.print_warning(f"Aucun résultat pour « {query} ».")
        _pause()
        return None
    return run_command_list(f"🔎 Résultats pour « {query} »", found,
                            subtitle=f"{len(found)} commande(s) trouvée(s)")


def _build_actions() -> Tuple[List[Any], Dict[str, Action]]:
    """Construit les items du menu principal et la table clé → action."""
    items: List[Any] = []
    actions: Dict[str, Action] = {}
    for i, (key, meta) in enumerate(catalog.CATEGORIES.items(), 1):
        count = len(catalog.get_by_category(key))
        items.append((str(i), f"{meta['icon']}  {meta['title']}",
                      f"{meta['description']} ({count})"))
        actions[str(i)] = (key, CATEGORY_VIEWS[key].run)
    n = len(catalog.CATEGORIES)
    favs = len([f for f in config.load_favorites() if catalog.get(f)])
    items += [None,
              (str(n + 1), "★  Favoris", f"{favs} commande(s) épinglée(s)"),
              (str(n + 2), "🔎 Rechercher", "Filtrer par nom ou description"),
              (str(n + 3), "ℹ  Infos", "Environnement, version, chemins"),
              None,
              ("q", "✗  Quitter", "")]
    actions[str(n + 1)] = ("fav", _show_favorites)
    actions[str(n + 2)] = ("search", _show_search)
    actions[str(n + 3)] = ("infos", _show_infos)
    actions["q"] = ("quit", lambda: "quit")
    actions["0"] = ("quit", lambda: "quit")  # alias discret
    return items, actions


def _draw(first: bool, items: List[Any]) -> None:
    """Dessine l'écran principal : header, bannière, menu, footer."""
    ui.clear()
    ui.print_header(compact=None if first else True)
    ui.print_banner()
    ui.print_menu("Menu principal", items)
    ui.print_footer()


def _confirm_quit() -> bool:
    """Ctrl+C au menu principal : demande confirmation (un second Ctrl+C quitte)."""
    ui.console.print()
    try:
        return ui.confirm("Quitter Termux API Studio ?", default=True)
    except KeyboardInterrupt:
        return True


def run() -> int:
    """Boucle principale du TUI. Ctrl+C ramène au menu au lieu de planter."""
    first = True
    while True:
        items, actions = _build_actions()
        _draw(first, items)
        first = False
        try:
            choice = ui.choose(actions.keys())
        except KeyboardInterrupt:
            if _confirm_quit():
                break
            continue
        try:
            outcome = actions[choice][1]()
        except KeyboardInterrupt:
            ui.console.print()
            ui.print_warning("Ctrl+C — retour au menu principal.")
            continue
        if outcome == "quit":
            break
    ui.print_success("À bientôt ! 👋")
    ui.print_rule()
    return 0
