"""Vue « Communication » : SMS, contacts, journal d'appels, appels."""
from __future__ import annotations

from typing import Any, Dict, List

from rich.text import Text

import ui

from . import register_hook, run_category

CATEGORY = "communication"


@register_hook("termux-sms-list")
def _sms_summary(result: Dict[str, Any], args: List[str]) -> None:
    """Résumé : nombre de messages et non-lus."""
    data = result.get("data")
    if not isinstance(data, list):
        return
    unread = sum(1 for m in data if isinstance(m, dict) and m.get("read") is False)
    ui.console.print(Text(f"  ✉  {len(data)} message(s) · {unread} non lu(s)", style="muted"))


@register_hook("termux-call-log")
def _call_summary(result: Dict[str, Any], args: List[str]) -> None:
    """Résumé : appels manqués."""
    data = result.get("data")
    if not isinstance(data, list):
        return
    missed = sum(1 for c in data if isinstance(c, dict) and c.get("type") == "MISSED")
    ui.console.print(Text(f"  📞 {len(data)} appel(s) · {missed} manqué(s)", style="muted"))


def run() -> str:
    """Menu Communication. Retourne "back" ou "quit"."""
    return run_category(CATEGORY)
