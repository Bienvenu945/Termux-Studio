"""Vue « Matériel » : batterie, caméras, GPS, capteurs, Wi-Fi, téléphonie."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from rich.text import Text

import ui

from . import register_hook, run_category

CATEGORY = "hardware"


@register_hook("termux-battery-status")
def _battery_gauge(result: Dict[str, Any], args: List[str]) -> None:
    """Jauge de batterie + résumé (statut, température, santé)."""
    data = result.get("data")
    if not isinstance(data, dict) or "percentage" not in data:
        return
    ui.print_gauge("🔋 Batterie", float(data["percentage"]), 100, " %")
    resume = (f"  {data.get('status', '?')} · {data.get('temperature', '?')} °C"
              f" · santé {data.get('health', '?')} · {data.get('plugged', '?')}")
    ui.console.print(Text(resume, style="muted"))


@register_hook("termux-wifi-connectioninfo")
def _wifi_gauge(result: Dict[str, Any], args: List[str]) -> None:
    """Jauge de qualité du signal Wi-Fi (RSSI −100 dBm → 0 %, −50 dBm → 100 %)."""
    data = result.get("data")
    if not isinstance(data, dict) or "rssi" not in data:
        return
    quality = max(0.0, min(100.0, (float(data["rssi"]) + 100) * 2))
    ui.print_gauge("📶 Signal", quality, 100, " %")
    ui.console.print(Text(f"  {data.get('ssid', '?')} · {data['rssi']} dBm", style="muted"))


@register_hook("termux-location")
def _location_link(result: Dict[str, Any], args: List[str]) -> None:
    """Lien OpenStreetMap vers la position obtenue."""
    data = result.get("data")
    if not isinstance(data, dict) or "latitude" not in data or "longitude" not in data:
        return
    lat, lon = data["latitude"], data["longitude"]
    ui.console.print(Text.assemble(("🗺  Carte : ", "key"),
                                   (f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}",
                                    "primary")))


@register_hook("termux-camera-photo")
def _photo_info(result: Dict[str, Any], args: List[str]) -> None:
    """Indique si le fichier photo a bien été écrit."""
    if not args:
        return
    path = Path(args[-1]).expanduser()
    if path.is_file():
        ui.print_success(f"Photo enregistrée : {path} ({path.stat().st_size // 1024} Ko)")
    else:
        ui.console.print(Text(f"  Aucun fichier trouvé à {path} (mode démo ou permission refusée).",
                              style="muted"))


def run() -> str:
    """Menu Matériel. Retourne "back" ou "quit"."""
    return run_category(CATEGORY)
