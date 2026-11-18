"""Exécution sécurisée des commandes termux-* (sans shell) et normalisation des résultats.

Toutes les fonctions retournent un dict : {ok, data, raw, error, duration_ms}.
Ce module n'importe PAS Rich.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import catalog
import config

Result = Dict[str, Any]

# Seuls des noms « termux-xxx » sont acceptés : impossible de lancer un autre binaire
_NAME_RE = re.compile(r"^termux-[a-z0-9-]+$")


def _result(ok: bool, data: Any = None, raw: str = "", error: str = "",
            duration_ms: int = 0) -> Result:
    """Construit le dict de résultat standard."""
    return {"ok": ok, "data": data, "raw": raw, "error": error, "duration_ms": duration_ms}


def _ms(start: float) -> int:
    """Millisecondes écoulées depuis `start` (perf_counter)."""
    return int((time.perf_counter() - start) * 1000)


def parse_output(raw: str) -> Any:
    """Parse la sortie en JSON structuré (dict/list) ; None si ce n'est pas du JSON."""
    text = raw.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except (ValueError, TypeError):
        return None
    return parsed if isinstance(parsed, (dict, list)) else None


def _api_error(data: Any) -> str:
    """Détecte les erreurs que termux-api renvoie en JSON avec un code retour 0."""
    if isinstance(data, dict) and len(data) == 1:
        for key in ("error", "API_ERROR"):
            if data.get(key):
                return str(data[key])
    return ""


def expand_args(args: Optional[List[Any]]) -> List[str]:
    """Convertit en str et développe '~' (uniquement '~' ou '~/…')."""
    out = []
    for a in args or []:
        s = str(a)
        out.append(os.path.expanduser(s) if s == "~" or s.startswith("~/") else s)
    return out


def _from_process(proc: "subprocess.CompletedProcess[str]", duration: int) -> Result:
    """Transforme un CompletedProcess en résultat standard."""
    raw = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    data = parse_output(raw)
    if proc.returncode != 0:
        return _result(False, data, raw, err or f"Code de retour {proc.returncode}", duration)
    api_err = _api_error(data)
    if api_err:
        return _result(False, data, raw, api_err, duration)
    return _result(True, data, raw, "", duration)


def _run_real(name: str, args: List[str], timeout: int) -> Result:
    """Exécute vraiment la commande (subprocess, sans shell)."""
    exe_name = config.EXEC_ALIASES.get(name, name)
    exe = shutil.which(exe_name)
    if exe is None:
        return _result(False, error=(f"Commande introuvable : {exe_name}. "
                                     "Installe-la avec : pkg install termux-api"))
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            [exe] + args, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, stdin=subprocess.DEVNULL, check=False)
    except subprocess.TimeoutExpired:
        return _result(False, error=(f"Délai dépassé ({timeout} s). Vérifie que l'app "
                                     "Termux:API est installée et que la permission est accordée."),
                       duration_ms=_ms(start))
    except FileNotFoundError:
        return _result(False, error=f"Commande introuvable : {exe_name}", duration_ms=_ms(start))
    except OSError as exc:
        return _result(False, error=f"Impossible d'exécuter {exe_name} : {exc}",
                       duration_ms=_ms(start))
    return _from_process(proc, _ms(start))


def _run_demo(name: str, args: List[str]) -> Result:
    """Simule la commande avec des données fictives (mode --demo)."""
    start = time.perf_counter()
    time.sleep(0.3)  # laisse voir le spinner
    value = catalog.get_demo(name, args)
    if isinstance(value, (dict, list)):
        return _result(True, value, json.dumps(value, ensure_ascii=False, indent=2),
                       duration_ms=_ms(start))
    if isinstance(value, str):
        return _result(True, None, value, duration_ms=_ms(start))
    return _result(True, None, "", duration_ms=_ms(start))


def _write_log(name: str, args: List[str], result: Result) -> None:
    """Écrit ~/.termux-studio/last_run.log (désactivable : TERMUX_STUDIO_NOLOG=1)."""
    if os.environ.get("TERMUX_STUDIO_NOLOG") or not config.ensure_dirs():
        return
    lines = [
        f"date        : {datetime.now().isoformat(timespec='seconds')}",
        f"commande    : {name} {' '.join(args)}".rstrip(),
        f"mode        : {'demo' if config.is_demo() else 'reel'}",
        f"ok          : {result['ok']}",
        f"duree_ms    : {result['duration_ms']}",
        f"erreur      : {result['error']}",
        "--- sortie ---",
        result["raw"][:8000],
    ]
    try:
        config.LOG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(config.LOG_FILE, 0o600)
    except OSError:
        pass  # le log est optionnel


def run_command(cmd_name: str, args: Optional[List[Any]] = None,
                timeout: Optional[int] = None, log: bool = True) -> Result:
    """Lance une commande termux-* et retourne {ok, data, raw, error, duration_ms}."""
    name = catalog.normalize_name(cmd_name)
    if not _NAME_RE.match(name):
        return _result(False, error=f"Nom de commande invalide : {cmd_name!r}")
    argv = expand_args(args)
    entry = catalog.get(name)
    effective = timeout or (entry["timeout"] if entry else config.DEFAULT_TIMEOUT)
    if config.is_demo():
        result = _run_demo(name, argv)
    else:
        result = _run_real(name, argv, effective)
    if log:
        _write_log(name, argv, result)
    return result
