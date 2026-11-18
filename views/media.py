"""Vue « Média » : synthèse vocale, lecteur audio, micro, dialogues, fond d'écran."""
from __future__ import annotations

from typing import Any, Dict, List

from rich.text import Text

import ui

from . import register_hook, run_category

CATEGORY = "media"


@register_hook("termux-microphone-record")
def _record_state(result: Dict[str, Any], args: List[str]) -> None:
    """Rappelle comment arrêter un enregistrement lancé."""
    if "-i" in args or "-q" in args:
        return
    ui.console.print(Text("  🎙  Pour arrêter : relance la commande et réponds « o » à l'arrêt.",
                          style="muted"))


def run() -> str:
    """Menu Média. Retourne "back" ou "quit"."""
    return run_category(CATEGORY)
