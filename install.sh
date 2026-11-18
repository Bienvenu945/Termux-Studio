#!/data/data/com.termux/files/usr/bin/bash
# Termux API Studio — installateur.
# Fallback desktop : ce script se relance tout seul avec /bin/bash si besoin
# (sur Linux, lance simplement :  bash install.sh).
if [ -z "${BASH_VERSION:-}" ]; then
  exec /bin/bash "$0" "$@"
fi

set -euo pipefail
cd "$(dirname "$0")"

# ── Couleurs ANSI basiques ────────────────────────────────────────────────────
CYAN=$'\033[1;36m'; MAGENTA=$'\033[1;35m'; YELLOW=$'\033[1;33m'
GREEN=$'\033[1;32m'; RED=$'\033[1;31m'; DIM=$'\033[2m'; RESET=$'\033[0m'

step() { printf "%s▶%s %s\n" "$CYAN" "$RESET" "$1"; }
ok()   { printf "  %s✓%s %s\n" "$GREEN" "$RESET" "$1"; }
warn() { printf "  %s⚠%s %s\n" "$YELLOW" "$RESET" "$1"; }
die()  { printf "  %s✗%s %s\n" "$RED" "$RESET" "$1" >&2; exit 1; }

printf "\n%s╔══════════════════════════════════════╗%s\n" "$MAGENTA" "$RESET"
printf "%s║%s   TERMUX API STUDIO · installation   %s║%s\n" "$MAGENTA" "$CYAN" "$MAGENTA" "$RESET"
printf "%s╚══════════════════════════════════════╝%s\n\n" "$MAGENTA" "$RESET"

IS_TERMUX=0
if [ -d "/data/data/com.termux/files/usr" ] || [ -n "${TERMUX_VERSION:-}" ]; then
  IS_TERMUX=1
fi

# ── 1. Paquets système (Termux) ──────────────────────────────────────────────
if [ "$IS_TERMUX" -eq 1 ]; then
  step "Environnement Termux détecté"
  if ! command -v python >/dev/null 2>&1; then
    step "Installation de python…"
    pkg install -y python
  fi
  ok "python présent"
  if ! command -v termux-battery-status >/dev/null 2>&1; then
    step "Installation de termux-api…"
    pkg install -y termux-api
  fi
  ok "termux-api présent"
  PY=python
else
  step "Environnement desktop détecté (mode démo recommandé)"
  command -v python3 >/dev/null 2>&1 || die "python3 est introuvable. Installe Python 3.9+."
  ok "python3 présent"
  warn "termux-api n'est utile que sur Android : utilise  python3 main.py --demo"
  PY=python3
fi

# ── 2. Dépendances Python ────────────────────────────────────────────────────
step "Installation des dépendances Python (rich)…"
RUN_PY="$PY"
if "$PY" -m pip install -r requirements.txt; then
  ok "rich installé"
else
  warn "pip refuse l'installation globale (environnement géré) → création d'un venv .venv"
  "$PY" -m venv .venv || die "Impossible de créer le venv (installe python3-venv)."
  .venv/bin/python -m pip install -r requirements.txt || die "Échec de l'installation de rich."
  RUN_PY=".venv/bin/python"
  ok "rich installé dans .venv"
fi

# ── 3. Droits d'exécution ────────────────────────────────────────────────────
chmod +x main.py
ok "main.py est exécutable"

# ── 4. Message final ─────────────────────────────────────────────────────────
printf "\n%s✔ Installation terminée !%s\n\n" "$GREEN" "$RESET"
printf "  Lancer le studio  : %s%s main.py%s\n" "$CYAN" "$RUN_PY" "$RESET"
printf "  Mode démo         : %s%s main.py --demo%s\n" "$CYAN" "$RUN_PY" "$RESET"
printf "  Vérifier l'env    : %s%s main.py --check%s\n\n" "$CYAN" "$RUN_PY" "$RESET"
if [ "$IS_TERMUX" -eq 1 ]; then
  printf "%s⚠ N'oublie pas :%s installe l'app %sTermux:API%s depuis F-Droid\n" "$YELLOW" "$RESET" "$MAGENTA" "$RESET"
  printf "  %shttps://f-droid.org/packages/com.termux.api/%s\n" "$DIM" "$RESET"
  printf "  puis accorde les permissions Android (SMS, localisation, caméra…).\n\n"
fi
