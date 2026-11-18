"""Helpers Rich réutilisables : header ASCII, panels, menus, tables, JSON, invites, spinner.

Toute l'interface passe par ce module (et donc par Rich).
"""
from __future__ import annotations

import json
import platform
import random
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Union

from rich import box
from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.json import JSON
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.prompt import Confirm, IntPrompt, InvalidResponse, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

import config

# Console globale, thème piloté par config.THEME
console = Console(theme=Theme(config.THEME), highlight=False)

MAX_TABLE_ROWS = 100
MAX_CARDS = 30

# ── Art ASCII « TERMUX / STUDIO » (statique, aucune dépendance) ──────────────
_GLYPHS: Dict[str, List[str]] = {
    "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
    "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
    "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
    "M": ["███╗   ███╗", "████╗ ████║", "██╔████╔██║", "██║╚██╔╝██║", "██║ ╚═╝ ██║",
          "╚═╝     ╚═╝"],
    "U": ["██╗   ██╗", "██║   ██║", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "X": ["██╗  ██╗", "╚██╗██╔╝", " ╚███╔╝ ", " ██╔██╗ ", "██╔╝ ██╗", "╚═╝  ╚═╝"],
    "S": ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"],
    "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    "O": [" ██████╗ ", "██╔═══██╗", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
}


def _render_word(word: str) -> List[str]:
    """Assemble les glyphes d'un mot en 6 lignes d'art ASCII."""
    return ["".join(_GLYPHS[ch][row] for ch in word) for row in range(6)]


_ART_TERMUX = _render_word("TERMUX")
_ART_STUDIO = _render_word("STUDIO")
_ART_WIDTH = max(len(line) for line in _ART_TERMUX)


# ── Couleurs et dégradés ─────────────────────────────────────────────────────
def _hex_to_rgb(color: str) -> tuple:
    h = color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _sample(stops: Sequence[str], t: float) -> str:
    """Couleur interpolée à la position t∈[0,1] le long des étapes du dégradé."""
    t = min(max(t, 0.0), 1.0)
    if len(stops) == 1:
        return stops[0]
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    frac = seg - i
    a, b = _hex_to_rgb(stops[i]), _hex_to_rgb(stops[i + 1])
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * frac) for x, y in zip(a, b))


def gradient_text(text: str, stops: Sequence[str], bold: bool = True) -> Text:
    """Texte dont chaque caractère a sa propre couleur (dégradé horizontal)."""
    out = Text()
    span = max(len(text) - 1, 1)
    for i, ch in enumerate(text):
        out.append(ch, style=f"{'bold ' if bold else ''}{_sample(stops, i / span)}")
    return out


def _gradient_art(lines: List[str], stops: Sequence[str]) -> Text:
    """Art ASCII avec un dégradé diagonal (colonne + ligne)."""
    width = max(len(line) for line in lines)
    out = Text(no_wrap=True)
    for r, line in enumerate(lines):
        for c, ch in enumerate(line.ljust(width)):
            if ch == " ":
                out.append(ch)
            else:
                t = (c / max(width - 1, 1)) * 0.85 + (r / max(len(lines) - 1, 1)) * 0.15
                out.append(ch, style=f"bold {_sample(stops, t)}")
        if r < len(lines) - 1:
            out.append("\n")
    return out


# ── Thème / écran ────────────────────────────────────────────────────────────
def apply_theme(name: str) -> bool:
    """Change la palette à la volée (cyan|magenta|mono)."""
    if not config.set_theme(name):
        return False
    console.push_theme(Theme(config.THEME))
    return True


def clear() -> None:
    """Efface l'écran (uniquement dans un vrai terminal)."""
    if console.is_terminal:
        console.clear()


def print_rule(title: Optional[str] = None) -> None:
    """Filet stylé qui clôt chaque écran."""
    label = Text(f" {title} ", style="title") if title else ""
    console.print(Rule(label, style="rule", characters="━"))


def badge(text: str, kind: str = "info") -> Text:
    """Petit badge de statut (kind : ok | err | demo | info)."""
    return Text(f" {text} ", style=f"badge.{kind}")


# ── En-têtes ─────────────────────────────────────────────────────────────────
def print_header(compact: Optional[bool] = None) -> None:
    """Affiche le header ASCII (complet si l'écran est assez grand, sinon compact)."""
    if compact is None:
        compact = console.width < _ART_WIDTH + 4 or console.height < 30
    stops = config.gradient_stops()
    if compact:
        console.print(Align.center(gradient_text("◢◤ TERMUX STUDIO ◥◣", stops)))
        return
    console.print()
    console.print(Align.center(_gradient_art(_ART_TERMUX, stops)))
    console.print(Align.center(_gradient_art(_ART_STUDIO, stops)))
    console.print(Align.center(gradient_text("⚡ termux-api · explorer · exécuter · visualiser ⚡",
                                             stops, bold=False)))


def print_banner() -> None:
    """Panel avec nom, version et tagline."""
    body = Group(
        Align.center(Text.assemble((config.APP_NAME, "title"), (f"  v{config.APP_VERSION}", "accent"))),
        Align.center(Text(config.APP_TAGLINE, style="muted italic")),
    )
    env = "📱 Termux" if config.is_termux() else "🖥  Desktop"
    py = "" if console.width < 64 else f" · 🐍 Python {platform.python_version()}"
    sub = Text.assemble((f" {env}{py} ", "muted"))
    if config.is_demo():
        sub.append_text(badge("MODE DÉMO", "demo"))
    console.print(Panel(body, box=box.DOUBLE, border_style="border", padding=(0, 2),
                        title=Text(" ✦ TERMUX API STUDIO ✦ ", style="secondary"),
                        subtitle=sub))


def print_footer(tip: Optional[str] = None) -> None:
    """Footer persistant avec une astuce rotative."""
    tip = tip or random.choice(config.TIPS)
    console.print(Rule(style="border.alt", characters="─"))
    console.print(Text.assemble(("💡 Astuce : ", "accent"), (tip, "muted")), justify="center")


# ── Menus ────────────────────────────────────────────────────────────────────
MenuItem = Optional[Sequence[str]]


def _unpack_item(idx: int, item: Sequence[str]) -> tuple:
    """(clé, libellé, description) à partir d'un tuple de 2 ou 3 éléments."""
    if len(item) == 3:
        return item[0], item[1], item[2]
    return str(idx), item[0], item[1]


def print_menu(title: str, items: Sequence[MenuItem], subtitle: Optional[str] = None) -> None:
    """Panel + table numérotée. Un item peut être (libellé, desc), (clé, libellé, desc) ou None (séparateur)."""
    narrow = console.width < 64
    grid = Table.grid(padding=(0, 1), expand=True)
    grid.add_column(no_wrap=True, justify="right")
    grid.add_column(ratio=1)
    if not narrow:
        grid.add_column(ratio=2)
    for idx, item in enumerate(items, 1):
        if item is None:
            grid.add_row(*([""] * (2 if narrow else 3)))
            continue
        key, label, desc = _unpack_item(idx, item)
        key_txt = Text(f"[{key}]", style="key")
        if narrow:
            cell = Text(label, style="primary")
            if desc:
                cell.append("\n" + desc, style="muted")
            grid.add_row(key_txt, cell)
        else:
            grid.add_row(key_txt, Text(label, style="primary"), Text(desc, style="muted"))
    console.print(Panel(grid, box=box.ROUNDED, border_style="border", padding=(1, 2),
                        title=Text(f" {title} ", style="title"),
                        subtitle=Text(subtitle, style="muted") if subtitle else None))
    print_rule()


def print_command_line(text: str) -> None:
    """Affiche la ligne de commande exécutée (style prompt shell)."""
    console.print(Text.assemble(("$ ", "secondary"), (text, "muted")))


def print_command_card(name: str, entry: Dict[str, Any]) -> None:
    """Fiche d'une commande : description, permission, nombre de paramètres."""
    body = Text(entry["description"] + "\n", style="text")
    if entry.get("permission"):
        body.append("🔐 Permission Android : ", style="muted")
        body.append(entry["permission"] + "\n", style="accent")
    n = len(entry.get("args", []))
    body.append(f"⚙  {n} paramètre(s) · ⏱ timeout {entry.get('timeout')} s", style="muted")
    sub = badge("ROOT", "err") if entry.get("requires_root") else None
    console.print(Panel(body, box=box.ROUNDED, border_style="border.alt", padding=(0, 2),
                        title=Text(f" {name} ", style="title"), subtitle=sub))


# ── Messages ─────────────────────────────────────────────────────────────────
def _as_renderable(msg: Union[str, RenderableType], style: str = "text") -> RenderableType:
    """Les chaînes deviennent du Text (aucune interprétation du markup)."""
    return Text(msg, style=style) if isinstance(msg, str) else msg


def _message_panel(icon: str, msg: Union[str, RenderableType], style: str, border: str,
                   title: str) -> None:
    body = Text.assemble((f"{icon} ", style))
    if isinstance(msg, str):
        body.append(msg, style=style)
        content: RenderableType = body
    else:
        content = Group(body, msg)
    console.print(Panel(content, border_style=border, box=box.ROUNDED, padding=(0, 2),
                        title=Text(f" {title} ", style=style)))


def print_error(msg: Union[str, RenderableType]) -> None:
    """Panel rouge avec icône ✗."""
    _message_panel("✗", msg, "error", "border.err", "ERREUR")


def print_success(msg: Union[str, RenderableType]) -> None:
    """Panel vert avec icône ✓."""
    _message_panel("✓", msg, "success", "border.ok", "SUCCÈS")


def print_warning(msg: Union[str, RenderableType]) -> None:
    """Panel jaune avec icône ⚠."""
    _message_panel("⚠", msg, "warning", "border.warn", "ATTENTION")


def print_env_alert(env: Dict[str, Any]) -> None:
    """Alerte détaillée quand termux-api est absent."""
    body = Text()
    body.append("termux-api est introuvable sur ce système.\n\n", style="error")
    if env.get("termux"):
        body.append("1. Installe le paquet :\n   ", style="text")
        body.append("pkg install termux-api\n\n", style="accent")
        body.append("2. Installe l'application ", style="text")
        body.append("Termux:API", style="primary")
        body.append(" depuis F-Droid :\n   https://f-droid.org/packages/com.termux.api/\n\n", style="muted")
        body.append("3. Accorde les permissions Android (SMS, localisation, caméra…).", style="text")
    else:
        body.append("Hors Termux, les commandes réelles sont indisponibles.\n", style="text")
        body.append("Sur Android : pkg install termux-api + app Termux:API (F-Droid).\n\n", style="muted")
        body.append("Pour tester l'interface maintenant :  ", style="text")
        body.append("python main.py --demo", style="accent")
    console.print(Panel(body, border_style="border.warn", box=box.HEAVY, padding=(1, 2),
                        title=Text(" ⚠ ENVIRONNEMENT INCOMPLET ", style="warning"),
                        subtitle=Text("pkg install termux-api", style="muted")))


def print_env_report(env: Dict[str, Any]) -> None:
    """Rapport complet sur l'environnement (utilisé par --check et le menu Infos)."""
    total = len(config.TERMUX_API_COMMANDS)
    rows = {
        "Application": f"{config.APP_NAME} v{config.APP_VERSION}",
        "Python": platform.python_version(),
        "Système": f"{platform.system()} {platform.machine()}",
        "Termux détecté": env.get("termux", False),
        "termux-api (battery-status)": env["ok"],
        "Commandes disponibles": f"{total - len(env['missing'])}/{total}",
        "Mode": "DÉMO (données fictives)" if config.is_demo() else "Réel",
        "Thème": config.current_theme(),
        "Dossier de données": str(config.DATA_DIR),
        "Chemin de l'application": str(Path(__file__).resolve().parent),
    }
    print_kv_table(rows, "Environnement")
    if not env["ok"]:
        print_env_alert(env)
    elif env["missing"]:
        names = ", ".join(env["missing"][:8]) + (" …" if len(env["missing"]) > 8 else "")
        print_warning(f"Commandes absentes : {names}")
    else:
        print_success("Environnement prêt : toutes les commandes sont disponibles.")
    print_rule()


# ── Résultats ────────────────────────────────────────────────────────────────
def is_table_data(data: Any) -> bool:
    """True si `data` est une liste non vide de dicts (affichable en table)."""
    return isinstance(data, list) and bool(data) and all(isinstance(r, dict) for r in data)


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _fmt_cell(value: Any) -> Text:
    """Formate une valeur de cellule (booléens, None, structures imbriquées)."""
    if value is None:
        return Text("—", style="muted")
    if isinstance(value, bool):
        return Text("✓" if value else "✗", style="success" if value else "error")
    if isinstance(value, (dict, list)):
        return Text(_truncate(json.dumps(value, ensure_ascii=False), 60), style="muted")
    return Text(_truncate(str(value), 140), style="value")


def _collect_columns(rows: List[Dict[str, Any]]) -> List[str]:
    """Colonnes auto-détectées : union des clés dans l'ordre d'apparition."""
    cols: List[str] = []
    for row in rows:
        for key in row:
            if key not in cols:
                cols.append(key)
    return cols


def _build_table(rows: List[Dict[str, Any]], cols: List[str]) -> Table:
    """Table Rich à partir d'une liste de dicts."""
    caption = f"{len(rows)} ligne(s)"
    if len(rows) > MAX_TABLE_ROWS:
        caption += f" · {MAX_TABLE_ROWS} premières affichées"
    table = Table(box=box.SIMPLE_HEAVY, header_style="table.header", border_style="border.alt",
                  row_styles=["", "dim"], caption=caption, caption_style="muted")
    for col in cols:
        table.add_column(str(col), overflow="fold")
    for row in rows[:MAX_TABLE_ROWS]:
        table.add_row(*[_fmt_cell(row.get(col)) for col in cols])
    return table


def _build_cards(rows: List[Dict[str, Any]]) -> Group:
    """Une mini-fiche clé/valeur par ligne (lisible sur écran étroit quand il y a trop de colonnes)."""
    parts: List[RenderableType] = []
    for i, row in enumerate(rows[:MAX_CARDS], 1):
        grid = Table.grid(padding=(0, 1))
        grid.add_column(style="key", no_wrap=True)
        grid.add_column(overflow="fold")
        for key, value in row.items():
            grid.add_row(str(key), _fmt_cell(value))
        parts.append(Rule(Text(f"#{i}", style="muted"), style="border.alt", characters="·", align="left"))
        parts.append(grid)
    caption = f"{len(rows)} ligne(s)"
    if len(rows) > MAX_CARDS:
        caption += f" · {MAX_CARDS} premières affichées"
    parts.append(Text(caption, style="muted"))
    return Group(*parts)


def _build_rows_view(rows: List[Dict[str, Any]]) -> RenderableType:
    """Table si les colonnes tiennent à l'écran, sinon fiches : rien n'est jamais masqué."""
    cols = _collect_columns(rows)
    if len(cols) <= max(4, console.width // 12):
        return _build_table(rows, cols)
    return _build_cards(rows)


def _result_subtitle(result: Dict[str, Any]) -> Text:
    sub = Text(f" ⏱ {result.get('duration_ms', 0)} ms ", style="muted")
    if config.is_demo():
        sub.append_text(badge("DÉMO", "demo"))
    return sub


def _print_failure(result: Dict[str, Any], title: str) -> None:
    body = Text.assemble(("✗ ", "error"), (result.get("error") or "Erreur inconnue", "error"))
    if result.get("raw"):
        body.append("\n\nSortie :\n", style="muted")
        body.append(_truncate(result["raw"], 600), style="text")
    console.print(Panel(body, border_style="border.err", box=box.HEAVY, padding=(0, 2),
                        title=Text(f" {title} ", style="error"),
                        subtitle=_result_subtitle(result)))


def print_result(result: Dict[str, Any], title: str = "Résultat", as_json: bool = False) -> None:
    """Affiche un résultat : JSON coloré, table auto (liste de dicts), texte brut ou erreur."""
    if not result.get("ok"):
        _print_failure(result, title)
        print_rule()
        return
    data, raw = result.get("data"), result.get("raw", "")
    border = "border"
    if data is None and not raw:
        body: RenderableType = Text("✓ Commande exécutée — aucune sortie.", style="success")
        border = "border.ok"
    elif is_table_data(data) and not as_json:
        body = _build_rows_view(data)
    elif data is not None:
        body = JSON.from_data(data, indent=2, ensure_ascii=False)
    else:
        body = Text(raw, style="text")
    console.print(Panel(body, border_style=border, box=box.ROUNDED, padding=(0, 1),
                        title=Text(f" {title} ", style="title"),
                        subtitle=_result_subtitle(result)))
    print_rule()


def print_kv_table(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """Table clé/valeur stylée."""
    table = Table(box=box.ROUNDED, show_header=False, border_style="border",
                  title=Text(f" {title} ", style="title") if title else None, expand=False)
    table.add_column(style="key", no_wrap=True)
    table.add_column(overflow="fold")
    for key, value in data.items():
        table.add_row(str(key), _fmt_cell(value))
    console.print(table)


def print_gauge(label: str, value: float, maximum: float = 100.0, suffix: str = "") -> None:
    """Jauge colorée (vert > 50 %, jaune > 20 %, rouge sinon)."""
    ratio = 0.0 if maximum <= 0 else max(0.0, min(1.0, value / maximum))
    style = "gauge.good" if ratio >= 0.5 else "gauge.mid" if ratio >= 0.2 else "gauge.low"
    width = max(10, min(30, console.width - 34))
    bar = ProgressBar(total=100, completed=ratio * 100, width=width, style="muted",
                      complete_style=style, finished_style=style)
    grid = Table.grid(padding=(0, 1))
    grid.add_column(style="key", no_wrap=True, min_width=12)
    grid.add_column()
    grid.add_column(no_wrap=True)
    shown = int(value) if float(value).is_integer() else round(value, 1)
    grid.add_row(label, bar, Text(f"{shown}{suffix}", style=style))
    console.print(grid)


# ── Saisie ───────────────────────────────────────────────────────────────────
class _FrPrompt(Prompt):
    """Prompt avec messages d'erreur en français."""
    illegal_choice_message = "[prompt.invalid.choice]Choisis une des options proposées"


class _FrIntPrompt(IntPrompt):
    """IntPrompt avec message d'erreur en français."""
    validate_error_message = "[prompt.invalid]Entre un nombre entier valide"


class _FrConfirm(Confirm):
    """Confirm oui/non en français (o/n)."""
    choices = ["o", "n"]
    validate_error_message = "[prompt.invalid]Réponds par o (oui) ou n (non)"

    def process_response(self, value: str) -> bool:  # type: ignore[override]
        v = value.strip().lower()
        if v in ("o", "oui", "y", "yes"):
            return True
        if v in ("n", "non", "no"):
            return False
        raise InvalidResponse(self.validate_error_message)


def _prompt_text(prompt: str) -> Text:
    return Text.assemble(("❯ ", "secondary"), (prompt, "prompt"))


def ask(prompt: str, default: Optional[str] = None, choices: Optional[List[str]] = None) -> str:
    """Pose une question texte. Entrée vide → default (ou chaîne vide)."""
    try:
        value = _FrPrompt.ask(_prompt_text(prompt), console=console,
                              default=default if default is not None else "",
                              show_default=default is not None, choices=choices)
    except EOFError:
        raise KeyboardInterrupt from None
    return value.strip()


def ask_int(prompt: str, default: Optional[int] = None, min_value: Optional[int] = None,
            max_value: Optional[int] = None) -> int:
    """Pose une question numérique (entier), avec bornes optionnelles."""
    while True:
        try:
            if default is None:
                value = _FrIntPrompt.ask(_prompt_text(prompt), console=console)
            else:
                value = _FrIntPrompt.ask(_prompt_text(prompt), console=console, default=default)
        except EOFError:
            raise KeyboardInterrupt from None
        if (min_value is None or value >= min_value) and (max_value is None or value <= max_value):
            return value
        console.print(Text(f"  ✗ La valeur doit être entre {min_value} et {max_value}.", style="error"))


def ask_secret(prompt: str) -> str:
    """Pose une question avec saisie masquée."""
    try:
        return _FrPrompt.ask(_prompt_text(prompt), console=console, password=True)
    except EOFError:
        raise KeyboardInterrupt from None


def confirm(prompt: str, default: bool = False) -> bool:
    """Confirmation oui/non."""
    try:
        return bool(_FrConfirm.ask(_prompt_text(prompt), console=console, default=default))
    except EOFError:
        raise KeyboardInterrupt from None


def choose(valid: Iterable[str], prompt: str = "Choix", default: Optional[str] = None) -> str:
    """Demande une clé de menu parmi `valid` (insensible à la casse) ; redemande si invalide."""
    valid_set = {str(v).lower() for v in valid}
    while True:
        answer = ask(prompt, default=default).lower()
        if answer in valid_set:
            return answer
        console.print(Text(f"  ✗ Choix invalide : « {answer} »", style="error"))


@contextmanager
def with_spinner(text: str, spinner: str = "dots12") -> Iterator[None]:
    """Context manager : spinner animé pendant une opération longue."""
    with console.status(Text(text, style="primary"), spinner=spinner, spinner_style="accent"):
        yield
