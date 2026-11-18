"""Vue « Système » : presse-papier, notifications, volume, téléchargements, stockage."""
from __future__ import annotations

from typing import Any, Dict, List

import ui

from . import register_hook, run_category

CATEGORY = "system"


@register_hook("termux-volume")
def _volume_gauges(result: Dict[str, Any], args: List[str]) -> None:
    """Une jauge par flux audio (quand la commande liste les volumes)."""
    data = result.get("data")
    if not ui.is_table_data(data):
        return
    for row in data:
        if "stream" in row and "volume" in row and "max_volume" in row:
            ui.print_gauge(f"🔊 {row['stream']}", float(row["volume"]), float(row["max_volume"]))


def run() -> str:
    """Menu Système. Retourne "back" ou "quit"."""
    return run_category(CATEGORY)
