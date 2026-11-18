"""Configuration globale de Termux API Studio : constantes, thèmes, environnement, favoris.

Ce module n'importe PAS Rich : il reste utilisable partout (--version, --check).
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

# ── Identité de l'application ────────────────────────────────────────────────
APP_NAME = "Termux API Studio"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Pilote ton Android depuis le terminal — termux-api, version badass."

# ── Dossiers / fichiers de données (~/.termux-studio/) ───────────────────────
DATA_DIR = Path.home() / ".termux-studio"
LOG_FILE = DATA_DIR / "last_run.log"
FAVORITES_FILE = DATA_DIR / "favorites.json"

DEFAULT_TIMEOUT = 20  # secondes, si le catalogue ne précise rien

# ── Thèmes : palettes (cyan / magenta / mono) ────────────────────────────────
PALETTES: Dict[str, Dict[str, str]] = {
    "cyan": {
        "primary": "#00d9ff", "secondary": "#ff00aa", "accent": "#ffd700",
        "success": "#00ff88", "error": "#ff3355", "muted": "#7f8c9b", "text": "#e6edf3",
    },
    "magenta": {
        "primary": "#ff00aa", "secondary": "#00d9ff", "accent": "#ffd700",
        "success": "#00ff88", "error": "#ff3355", "muted": "#8f7f9b", "text": "#f3e6ee",
    },
    "mono": {
        "primary": "#ffffff", "secondary": "#bdbdbd", "accent": "#ffffff",
        "success": "#e0e0e0", "error": "#ffffff", "muted": "#808080", "text": "#d0d0d0",
    },
}

# Dégradés (couleurs-étapes) utilisés par le header ASCII
GRADIENTS: Dict[str, List[str]] = {
    "cyan": ["#00d9ff", "#ff00aa", "#ffd700"],
    "magenta": ["#ff00aa", "#ffd700", "#00d9ff"],
    "mono": ["#ffffff", "#8a8a8a"],
}

_STATE: Dict[str, Any] = {"theme": "cyan", "demo": False}


def _build_theme(name: str) -> Dict[str, str]:
    """Construit le dict de styles Rich pour une palette donnée."""
    p = PALETTES[name]
    return {
        # styles sémantiques
        "primary": f"bold {p['primary']}", "secondary": f"bold {p['secondary']}",
        "accent": f"bold {p['accent']}", "success": f"bold {p['success']}",
        "error": f"bold {p['error']}", "warning": f"bold {p['accent']}",
        "muted": p["muted"], "text": p["text"], "title": f"bold {p['primary']}",
        "key": f"bold {p['secondary']}", "value": p["text"], "tip": f"italic {p['accent']}",
        # bordures et filets
        "border": p["primary"], "border.alt": p["secondary"], "border.ok": p["success"],
        "border.err": p["error"], "border.warn": p["accent"], "rule": p["secondary"],
        # invites (rich.prompt)
        "prompt": f"bold {p['primary']}", "prompt.default": p["muted"],
        "prompt.choices": p["accent"], "prompt.invalid": p["error"],
        "prompt.invalid.choice": p["error"],
        # coloration JSON (rich.json)
        "json.brace": f"bold {p['text']}", "json.str": p["success"],
        "json.number": p["accent"], "json.bool_true": f"bold {p['success']}",
        "json.bool_false": f"bold {p['error']}", "json.null": f"italic {p['secondary']}",
        "json.key": f"bold {p['primary']}",
        # badges et jauges
        "badge.ok": f"bold #000000 on {p['success']}", "badge.err": f"bold #000000 on {p['error']}",
        "badge.demo": f"bold #000000 on {p['accent']}", "badge.info": f"bold #000000 on {p['primary']}",
        "gauge.good": p["success"], "gauge.mid": p["accent"], "gauge.low": p["error"],
        "table.header": f"bold {p['primary']}",
    }


# THEME : dict de styles Rich actif (modifié en place par set_theme)
THEME: Dict[str, str] = _build_theme("cyan")


def set_theme(name: str) -> bool:
    """Active une palette (cyan|magenta|mono). Retourne False si inconnue."""
    if name not in PALETTES:
        return False
    THEME.clear()
    THEME.update(_build_theme(name))
    _STATE["theme"] = name
    return True


def current_theme() -> str:
    """Nom du thème actif."""
    return _STATE["theme"]


def gradient_stops() -> List[str]:
    """Couleurs du dégradé du thème actif."""
    return GRADIENTS[_STATE["theme"]]


def set_demo(flag: bool) -> None:
    """Active/désactive le mode démo (fausses données, aucune commande exécutée)."""
    _STATE["demo"] = bool(flag)


def is_demo() -> bool:
    """True si le mode démo est actif."""
    return bool(_STATE["demo"])


# ── Commandes termux-api attendues ───────────────────────────────────────────
TERMUX_API_COMMANDS: List[str] = [
    # hardware
    "termux-battery-status", "termux-camera-info", "termux-camera-photo",
    "termux-fingerprint", "termux-location", "termux-sensor", "termux-torch",
    "termux-vibrate", "termux-wifi-connectioninfo", "termux-wifi-scaninfo",
    "termux-wifi-enable", "termux-telephony-deviceinfo", "termux-telephony-cellinfo",
    # communication
    "termux-sms-list", "termux-sms-send", "termux-contact-list", "termux-call-log",
    "termux-telephony-call",
    # system
    "termux-clipboard-get", "termux-clipboard-set", "termux-notification",
    "termux-notification-remove", "termux-notification-list", "termux-toast",
    "termux-volume", "termux-brightness", "termux-download", "termux-job-scheduler",
    "termux-share", "termux-storage-get", "termux-storage-list",
    # media
    "termux-tts-speak", "termux-tts-engines", "termux-media-player", "termux-media-scan",
    "termux-microphone-record", "termux-dialog", "termux-wallpaper", "termux-audio-info",
    "termux-speech-to-text",
]

# Certaines entrées du catalogue s'exécutent via un binaire différent.
# `termux-storage-list` n'existe pas dans termux-api : on liste les dossiers SAF autorisés.
EXEC_ALIASES: Dict[str, str] = {"termux-storage-list": "termux-saf-dirs"}

# ── Astuces rotatives (footer du menu principal) ─────────────────────────────
TIPS: List[str] = [
    "termux-sms-send nécessite la permission SMS pour Termux:API.",
    "Ajoute --demo pour tester l'interface sans téléphone ni Termux.",
    "termux-location peut prendre plusieurs secondes : patience, le GPS se réveille.",
    "Lance directement une catégorie : python main.py --category hardware",
    "Mode CLI direct : python main.py --run termux-battery-status",
    "Épingle tes commandes préférées : python main.py --fav add termux-torch",
    "Change de palette avec --theme cyan | magenta | mono.",
    "Le dernier appel est loggé dans ~/.termux-studio/last_run.log.",
    "Si une commande se fige, vérifie que l'app Termux:API est bien installée.",
    "termux-wifi-scaninfo requiert la permission de localisation.",
    "Dans Termux, exécute termux-setup-storage pour accéder à /sdcard.",
    "Ctrl+C te ramène au menu précédent sans quitter le studio.",
]


# ── Environnement ────────────────────────────────────────────────────────────
def is_termux() -> bool:
    """Détecte un environnement Termux (Android)."""
    return "com.termux" in os.environ.get("PREFIX", "") or os.path.isdir("/data/data/com.termux")


def ensure_dirs() -> bool:
    """Crée ~/.termux-studio/ si besoin. Retourne False si impossible."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def check_environment() -> Dict[str, Any]:
    """Vérifie la présence de termux-api. Retourne {ok, missing, hint, termux}."""
    missing = [c for c in TERMUX_API_COMMANDS
               if shutil.which(EXEC_ALIASES.get(c, c)) is None]
    ok = shutil.which("termux-battery-status") is not None
    if ok:
        hint = "Environnement prêt."
    elif is_termux():
        hint = ("Installe le paquet : pkg install termux-api — puis l'application "
                "Termux:API (F-Droid) et accorde les permissions Android.")
    else:
        hint = ("Environnement non-Termux : les commandes termux-* sont indisponibles. "
                "Utilise --demo pour explorer l'interface avec des données fictives.")
    return {"ok": ok, "missing": missing, "hint": hint, "termux": is_termux()}


# ── Favoris (~/.termux-studio/favorites.json) ────────────────────────────────
def load_favorites() -> List[str]:
    """Lit la liste des favoris (liste vide si absent ou corrompu)."""
    try:
        data = json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
        favs = data.get("favorites", []) if isinstance(data, dict) else []
        return [f for f in favs if isinstance(f, str)]
    except (OSError, ValueError):
        return []


def save_favorites(favs: List[str]) -> bool:
    """Écrit la liste des favoris. Retourne False en cas d'échec."""
    if not ensure_dirs():
        return False
    try:
        FAVORITES_FILE.write_text(
            json.dumps({"favorites": favs}, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError:
        return False


def is_favorite(cmd: str) -> bool:
    """True si la commande est en favori."""
    return cmd in load_favorites()


def add_favorite(cmd: str) -> bool:
    """Ajoute un favori. False si déjà présent ou échec d'écriture."""
    favs = load_favorites()
    if cmd in favs:
        return False
    return save_favorites(favs + [cmd])


def remove_favorite(cmd: str) -> bool:
    """Retire un favori. False si absent ou échec d'écriture."""
    favs = load_favorites()
    if cmd not in favs:
        return False
    return save_favorites([f for f in favs if f != cmd])
