"""Catalogue des commandes termux-* : métadonnées, arguments, recherche et données de démo.

Ce module n'importe PAS Rich. Chaque entrée de CATALOG suit ce schéma :
    category, description, args, timeout, requires_root
+ clés optionnelles : permission, also_in, confirm, hint.
"""
from __future__ import annotations

import unicodedata
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

DEFAULT_DIR = "~/.termux-studio"

# ── Catégories (affichage du menu) ───────────────────────────────────────────
CATEGORIES: Dict[str, Dict[str, str]] = {
    "hardware": {"title": "Matériel", "icon": "🔧",
                 "description": "Batterie, caméra, GPS, capteurs, Wi-Fi, téléphonie"},
    "communication": {"title": "Communication", "icon": "💬",
                      "description": "SMS, contacts, journal d'appels, appels"},
    "system": {"title": "Système", "icon": "🧩",
               "description": "Presse-papier, notifications, volume, téléchargements"},
    "media": {"title": "Média", "icon": "🎵",
              "description": "Voix, lecteur audio, micro, dialogues, fond d'écran"},
}


def _arg(name: str, prompt: str, required: bool = False, secret: bool = False,
         flag: Optional[str] = None, kind: str = "text", default: Optional[str] = None,
         choices: Optional[List[str]] = None, when: Optional[Dict[str, Any]] = None,
         when_set: Optional[str] = None) -> Dict[str, Any]:
    """Construit la description d'un argument.

    kind : text | int | number | bool | choice
    flag : option (ex. "-c") ; None = argument positionnel
    when : conditions {argument: valeur | [valeurs]} pour poser la question
    when_set : ne poser la question que si cet argument a été renseigné
    """
    return {"name": name, "prompt": prompt, "required": required, "secret": secret,
            "flag": flag, "type": kind, "default": default, "choices": choices,
            "when": when or {}, "when_set": when_set}


def _cmd(category: str, description: str, args: Optional[List[Dict[str, Any]]] = None,
         timeout: int = 15, requires_root: bool = False, permission: Optional[str] = None,
         also_in: Optional[List[str]] = None, confirm: Optional[str] = None,
         hint: Optional[str] = None) -> Dict[str, Any]:
    """Construit une entrée du catalogue."""
    return {"category": category, "description": description, "args": args or [],
            "timeout": timeout, "requires_root": requires_root, "permission": permission,
            "also_in": also_in or [], "confirm": confirm, "hint": hint}


CATALOG: Dict[str, Dict[str, Any]] = {
    # ══ HARDWARE ═════════════════════════════════════════════════════════════
    "termux-battery-status": _cmd(
        "hardware", "État de la batterie (niveau, température, santé)"),
    "termux-camera-info": _cmd(
        "hardware", "Informations sur les caméras (id, orientation, résolutions)",
        permission="Caméra"),
    "termux-camera-photo": _cmd(
        "hardware", "Prend une photo avec la caméra choisie",
        args=[_arg("camera", "ID de la caméra (0 = arrière, 1 = avant)", flag="-c", default="0"),
              _arg("file", "Fichier de sortie (.jpg)", required=True,
                   default=f"{DEFAULT_DIR}/photo.jpg")],
        timeout=30, permission="Caméra", also_in=["media"], hint="Prise de vue en cours…"),
    "termux-fingerprint": _cmd(
        "hardware", "Authentification par empreinte digitale",
        args=[_arg("title", "Titre de la boîte de dialogue", flag="-t",
                   default="Termux API Studio"),
              _arg("description", "Description affichée", flag="-d",
                   default="Authentifie-toi pour continuer")],
        timeout=60, permission="Biométrie", hint="Pose ton doigt sur le capteur…"),
    "termux-location": _cmd(
        "hardware", "Position GPS / réseau (latitude, longitude, précision)",
        args=[_arg("provider", "Fournisseur", flag="-p", kind="choice",
                   choices=["gps", "network", "passive"], default="network"),
              _arg("request", "Type de requête (last = dernière position connue)", flag="-r",
                   kind="choice", choices=["last", "once"], default="last")],
        timeout=60, permission="Localisation", hint="Acquisition de la position…"),
    "termux-sensor": _cmd(
        "hardware", "Lit les capteurs du téléphone (accéléromètre, gyroscope…)",
        args=[_arg("list", "Lister les capteurs disponibles ?", kind="bool", flag="-l"),
              _arg("sensors", "Capteurs à lire (ex: accelerometer,gyroscope)", required=True,
                   flag="-s", default="accelerometer", when={"list": False}),
              _arg("count", "Nombre de lectures", required=True, flag="-n", kind="int",
                   default="1", when={"list": False}),
              _arg("delay", "Délai entre lectures (ms)", flag="-d", kind="int",
                   default="500", when={"list": False})],
        timeout=30),
    "termux-torch": _cmd(
        "hardware", "Allume / éteint la lampe torche",
        args=[_arg("state", "État de la torche", required=True, kind="choice",
                   choices=["on", "off"], default="on")], permission="Caméra"),
    "termux-vibrate": _cmd(
        "hardware", "Fait vibrer le téléphone",
        args=[_arg("duration", "Durée en millisecondes", flag="-d", kind="int", default="500"),
              _arg("force", "Forcer même en mode silencieux ?", kind="bool", flag="-f")]),
    "termux-wifi-connectioninfo": _cmd(
        "hardware", "Infos sur la connexion Wi-Fi actuelle (SSID, IP, signal)"),
    "termux-wifi-scaninfo": _cmd(
        "hardware", "Scan des réseaux Wi-Fi alentour", timeout=30, permission="Localisation"),
    "termux-wifi-enable": _cmd(
        "hardware", "Active ou désactive le Wi-Fi",
        args=[_arg("state", "Wi-Fi activé ?", required=True, kind="choice",
                   choices=["true", "false"], default="true")], also_in=["system"]),
    "termux-telephony-deviceinfo": _cmd(
        "hardware", "Infos téléphonie : opérateur, réseau, état de la SIM",
        permission="Téléphone"),
    "termux-telephony-cellinfo": _cmd(
        "hardware", "Infos sur les antennes-relais (cellules) visibles",
        timeout=30, permission="Téléphone / Localisation"),

    # ══ COMMUNICATION ════════════════════════════════════════════════════════
    "termux-sms-list": _cmd(
        "communication", "Liste les SMS (inbox, envoyés, brouillons…)",
        args=[_arg("limit", "Nombre de messages", flag="-l", kind="int", default="10"),
              _arg("offset", "Décalage (offset)", flag="-o", kind="int", default="0"),
              _arg("type", "Boîte à lire", flag="-t", kind="choice",
                   choices=["all", "inbox", "sent", "draft", "outbox"], default="inbox")],
        timeout=30, permission="SMS"),
    "termux-sms-send": _cmd(
        "communication", "Envoie un SMS",
        args=[_arg("number", "Numéro du destinataire", required=True, flag="-n"),
              _arg("message", "Texte du message", required=True)],
        timeout=30, permission="SMS", confirm="Envoyer réellement ce SMS ?"),
    "termux-contact-list": _cmd(
        "communication", "Liste les contacts du téléphone", timeout=30, permission="Contacts"),
    "termux-call-log": _cmd(
        "communication", "Journal d'appels récent",
        args=[_arg("limit", "Nombre d'entrées", flag="-l", kind="int", default="10"),
              _arg("offset", "Décalage (offset)", flag="-o", kind="int", default="0")],
        timeout=30, permission="Journal d'appels"),
    "termux-telephony-call": _cmd(
        "communication", "Passe un appel téléphonique",
        args=[_arg("number", "Numéro à appeler", required=True)],
        permission="Téléphone", confirm="Lancer réellement cet appel ?"),

    # ══ SYSTEM ═══════════════════════════════════════════════════════════════
    "termux-clipboard-get": _cmd("system", "Lit le contenu du presse-papier"),
    "termux-clipboard-set": _cmd(
        "system", "Écrit du texte dans le presse-papier",
        args=[_arg("text", "Texte à copier", required=True)]),
    "termux-notification": _cmd(
        "system", "Affiche une notification Android",
        args=[_arg("title", "Titre", required=True, flag="-t", default="Termux API Studio"),
              _arg("content", "Contenu", required=True, flag="-c",
                   default="Hello depuis le studio !"),
              _arg("id", "Identifiant (pour la retirer ensuite)", flag="--id",
                   default="studio-1"),
              _arg("priority", "Priorité", flag="--priority", kind="choice",
                   choices=["default", "high", "low", "max", "min"], default="default"),
              _arg("sound", "Jouer un son ?", kind="bool", flag="--sound")]),
    "termux-notification-remove": _cmd(
        "system", "Retire une notification par son identifiant",
        args=[_arg("id", "Identifiant de la notification", required=True, default="studio-1")]),
    "termux-notification-list": _cmd(
        "system", "Liste les notifications actives", permission="Accès aux notifications"),
    "termux-toast": _cmd(
        "system", "Affiche un toast (message flottant)",
        args=[_arg("gravity", "Position", flag="-g", kind="choice",
                   choices=["top", "middle", "bottom"], default="middle"),
              _arg("short", "Toast court ?", kind="bool", flag="-s"),
              _arg("text", "Texte du toast", required=True, default="Salut depuis Termux Studio")]),
    "termux-volume": _cmd(
        "system", "Affiche ou règle les volumes audio",
        args=[_arg("stream", "Flux à régler (vide = lister les volumes)", kind="choice",
                   choices=["call", "system", "ring", "music", "alarm", "notification"]),
              _arg("volume", "Nouveau volume (entier)", required=True, kind="int",
                   when_set="stream")]),
    "termux-brightness": _cmd(
        "system", "Règle la luminosité de l'écran (0-255 ou auto)",
        args=[_arg("level", "Niveau 0-255 ou « auto »", required=True, default="auto")],
        permission="Modifier les paramètres système"),
    "termux-download": _cmd(
        "system", "Télécharge un fichier via le gestionnaire Android",
        args=[_arg("title", "Titre du téléchargement", flag="-t"),
              _arg("path", "Chemin de destination (optionnel)", flag="-p"),
              _arg("url", "URL à télécharger", required=True)],
        timeout=60, permission="Stockage"),
    "termux-job-scheduler": _cmd(
        "system", "Planifie un script périodique (JobScheduler Android)",
        args=[_arg("pending", "Lister les jobs en attente ?", kind="bool", flag="--pending"),
              _arg("script", "Script à exécuter", required=True, flag="--script",
                   default=f"{DEFAULT_DIR}/job.sh", when={"pending": False}),
              _arg("period", "Période en ms (min. 900000)", flag="--period-ms", kind="int",
                   default="900000", when={"pending": False}),
              _arg("job_id", "Identifiant du job", flag="--job-id", kind="int", default="1",
                   when={"pending": False})]),
    "termux-share": _cmd(
        "system", "Partage un fichier via le menu de partage Android",
        args=[_arg("action", "Action", flag="-a", kind="choice",
                   choices=["send", "edit", "view"], default="send"),
              _arg("title", "Titre (optionnel)", flag="-t"),
              _arg("file", "Fichier à partager", required=True)]),
    "termux-storage-get": _cmd(
        "system", "Ouvre le sélecteur de fichiers Android et copie le choix",
        args=[_arg("file", "Fichier de sortie", required=True,
                   default=f"{DEFAULT_DIR}/storage_get.out")],
        timeout=120, hint="Choisis un fichier dans le sélecteur Android…"),
    "termux-storage-list": _cmd(
        "system", "Liste les dossiers de stockage autorisés (SAF, via termux-saf-dirs)"),

    # ══ MEDIA ════════════════════════════════════════════════════════════════
    "termux-tts-speak": _cmd(
        "media", "Synthèse vocale : lit un texte à voix haute",
        args=[_arg("language", "Langue (ex: fr, en)", flag="-l", default="fr"),
              _arg("rate", "Vitesse (1.0 = normal)", flag="-r", kind="number", default="1.0"),
              _arg("text", "Texte à prononcer", required=True, default="Bonjour depuis Termux")],
        timeout=120),
    "termux-tts-engines": _cmd("media", "Liste les moteurs de synthèse vocale installés"),
    "termux-media-player": _cmd(
        "media", "Contrôle le lecteur audio (info, play, pause, stop)",
        args=[_arg("action", "Action", required=True, kind="choice",
                   choices=["info", "play", "pause", "stop"], default="info"),
              _arg("file", "Fichier audio à lire", required=True, when={"action": "play"})]),
    "termux-media-scan": _cmd(
        "media", "Demande à Android de (ré)indexer des fichiers média",
        args=[_arg("recursive", "Scan récursif ?", kind="bool", flag="-r"),
              _arg("path", "Fichier ou dossier", required=True, default="/sdcard/Download")],
        timeout=30, permission="Stockage"),
    "termux-microphone-record": _cmd(
        "media", "Enregistre le micro (ou affiche / stoppe l'enregistrement)",
        args=[_arg("info", "Afficher l'état de l'enregistrement ?", kind="bool", flag="-i"),
              _arg("stop", "Arrêter l'enregistrement en cours ?", kind="bool", flag="-q",
                   when={"info": False}),
              _arg("file", "Fichier de sortie", flag="-f", default=f"{DEFAULT_DIR}/record.m4a",
                   when={"info": False, "stop": False}),
              _arg("limit", "Durée max (secondes, 0 = illimité)", flag="-l", kind="int",
                   default="5", when={"info": False, "stop": False})],
        timeout=20, permission="Micro"),
    "termux-dialog": _cmd(
        "media", "Boîtes de dialogue Android (texte, confirmation, liste…)",
        args=[_arg("widget", "Type de dialogue", kind="choice",
                   choices=["text", "confirm", "checkbox", "counter", "date", "radio",
                            "sheet", "spinner", "speech", "time"], default="text"),
              _arg("title", "Titre", flag="-t", default="Termux API Studio"),
              _arg("hint", "Texte d'aide (placeholder)", flag="-i", when={"widget": "text"}),
              _arg("values", "Valeurs séparées par des virgules (ex: A,B,C)", required=True,
                   flag="-v", when={"widget": ["radio", "checkbox", "spinner", "sheet"]})],
        timeout=120, hint="Réponds sur l'écran du téléphone…"),
    "termux-wallpaper": _cmd(
        "media", "Change le fond d'écran (fichier ou URL)",
        args=[_arg("file", "Fichier image (vide = utiliser une URL)", flag="-f"),
              _arg("url", "URL de l'image", required=True, flag="-u", when={"file": ""}),
              _arg("lockscreen", "Appliquer à l'écran de verrouillage ?", kind="bool",
                   flag="-l")], timeout=30),
    "termux-audio-info": _cmd("media", "Infos sur le sous-système audio du téléphone"),
    "termux-speech-to-text": _cmd(
        "media", "Reconnaissance vocale : transcrit ce que tu dis",
        timeout=60, permission="Micro", hint="Parle maintenant…"),
}


# ── API du catalogue ─────────────────────────────────────────────────────────
def get_all() -> Dict[str, Dict[str, Any]]:
    """Retourne tout le catalogue (copie superficielle)."""
    return dict(CATALOG)


def get(name: str) -> Optional[Dict[str, Any]]:
    """Retourne l'entrée d'une commande (nom exact) ou None."""
    return CATALOG.get(name)


def get_by_category(cat: str) -> Dict[str, Dict[str, Any]]:
    """Commandes d'une catégorie ; les commandes partagées (`also_in`) viennent en dernier."""
    items = [(n, e) for n, e in CATALOG.items() if e["category"] == cat or cat in e["also_in"]]
    items.sort(key=lambda it: it[1]["category"] != cat)  # tri stable : propres d'abord
    return dict(items)


def normalize_name(name: str) -> str:
    """'battery-status' ou 'TERMUX-battery-status' → 'termux-battery-status'."""
    n = name.strip().lower()
    return n if n.startswith("termux-") else f"termux-{n}"


def _norm(text: str) -> str:
    """Minuscule + sans accents, pour une recherche tolérante."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def search(query: str) -> List[str]:
    """Noms de commandes dont le nom, la catégorie ou la description contiennent tous les mots."""
    tokens = _norm(query).split()
    if not tokens:
        return []
    found = []
    for name, entry in CATALOG.items():
        hay = _norm(f"{name} {entry['category']} {entry['description']}")
        if all(t in hay for t in tokens):
            found.append(name)
    return found


def build_args(name: str, values: Dict[str, Any]) -> List[str]:
    """Transforme les valeurs saisies en liste argv, dans l'ordre du catalogue."""
    entry = CATALOG.get(name)
    if entry is None:
        return []
    out: List[str] = []
    for arg in entry["args"]:
        val = values.get(arg["name"])
        if val is None or val is False or val == "":
            continue
        flag = arg.get("flag")
        if arg["type"] == "bool":
            if flag:
                out.append(flag)
        elif flag:
            out += [flag, str(val)]
        else:
            out.append(str(val))
    return out


# ── Données de démonstration (--demo) ────────────────────────────────────────
def _ago(minutes: int) -> str:
    """Date relative formatée (rend les données de démo vivantes)."""
    return (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")


def _flag_value(args: List[str], flag: str, default: int) -> int:
    """Valeur entière suivant un flag dans une liste argv."""
    try:
        return int(args[args.index(flag) + 1])
    except (ValueError, IndexError):
        return default


def _demo_sms(args: List[str]) -> List[Dict[str, Any]]:
    rows = [
        {"threadid": 12, "type": "inbox", "read": False, "sender": "Maman",
         "number": "+33600000001", "received": _ago(14), "body": "N'oublie pas le pain ce soir !"},
        {"threadid": 7, "type": "inbox", "read": True, "sender": "Banque",
         "number": "36000", "received": _ago(95), "body": "Votre code de vérification est 482913."},
        {"threadid": 3, "type": "inbox", "read": True, "sender": "Léa",
         "number": "+33600000002", "received": _ago(260), "body": "On se capte à 20h au ciné ? 🍿"},
        {"threadid": 9, "type": "inbox", "read": True, "sender": "Livraison",
         "number": "+33600000003", "received": _ago(1400), "body": "Votre colis arrive demain entre 9h et 12h."},
        {"threadid": 5, "type": "inbox", "read": True, "sender": "Hugo",
         "number": "+33600000004", "received": _ago(2900), "body": "Merci pour le coup de main, t'es un boss."},
    ]
    return rows[:max(1, _flag_value(args, "-l", 5))]


def _demo_calls(args: List[str]) -> List[Dict[str, Any]]:
    rows = [
        {"name": "Maman", "phone_number": "+33600000001", "type": "INCOMING",
         "date": _ago(40), "duration": "142"},
        {"name": "Léa", "phone_number": "+33600000002", "type": "OUTGOING",
         "date": _ago(310), "duration": "58"},
        {"name": "", "phone_number": "+33900000009", "type": "MISSED",
         "date": _ago(900), "duration": "0"},
        {"name": "Hugo", "phone_number": "+33600000004", "type": "INCOMING",
         "date": _ago(2100), "duration": "603"},
    ]
    return rows[:max(1, _flag_value(args, "-l", 4))]


def _demo_sensor(args: List[str]) -> Dict[str, Any]:
    if "-l" in args:
        return {"sensors": ["BMI160 Accelerometer", "BMI160 Gyroscope", "AK09911 Magnetometer",
                            "TCS3400 Light", "STK3x1x Proximity", "Pressure Sensor"]}
    return {"BMI160 Accelerometer": {"values": [0.12, 9.78, 0.31]}}


def _demo_volume(args: List[str]) -> Any:
    if args:
        return None
    return [{"stream": "call", "volume": 3, "max_volume": 5},
            {"stream": "system", "volume": 5, "max_volume": 7},
            {"stream": "ring", "volume": 4, "max_volume": 7},
            {"stream": "music", "volume": 9, "max_volume": 15},
            {"stream": "alarm", "volume": 5, "max_volume": 7},
            {"stream": "notification", "volume": 4, "max_volume": 7}]


def _demo_player(args: List[str]) -> Any:
    action = args[0] if args else "info"
    if action == "play":
        return f"Now Playing: {args[1] if len(args) > 1 else 'piste.mp3'}"
    if action == "info":
        return "Status: Playing\nTrack: /sdcard/Music/synthwave.mp3\nCurrent Position: 00:42 / 03:51"
    return f"Media player: {action} OK"


def _demo_record(args: List[str]) -> Any:
    if "-i" in args:
        return {"isRecording": False}
    if "-q" in args:
        return "Recording finished: ~/.termux-studio/record.m4a"
    return "Recording started: ~/.termux-studio/record.m4a"


def _demo_job(args: List[str]) -> str:
    if "--pending" in args:
        return "Pending Job 1: JobInfo{id=1, periodic=900000ms, script=job.sh}"
    return "Scheduled job 1 (période 900000 ms)"


def _demo_dialog(args: List[str]) -> Dict[str, Any]:
    widget = args[0] if args and not args[0].startswith("-") else "text"
    if widget == "confirm":
        return {"code": -1, "text": "yes"}
    if widget in ("radio", "spinner", "sheet"):
        return {"code": -1, "index": 1, "text": "B"}
    return {"code": -1, "text": "Hello depuis la démo"}


DEMO_DATA: Dict[str, Any] = {
    "termux-battery-status": {"health": "GOOD", "percentage": 87, "plugged": "UNPLUGGED",
                              "status": "DISCHARGING", "temperature": 29.4, "current": -412000},
    "termux-camera-info": [
        {"id": "0", "facing": "back", "focal_lengths": [4.38], "max_jpeg": "4000x3000",
         "flash": True},
        {"id": "1", "facing": "front", "focal_lengths": [2.46], "max_jpeg": "3264x2448",
         "flash": False}],
    "termux-fingerprint": {"errors": [], "failed_attempts": 0,
                           "auth_result": "AUTH_RESULT_SUCCESS"},
    "termux-location": {"latitude": 48.8566, "longitude": 2.3522, "altitude": 35.2,
                        "accuracy": 12.5, "bearing": 0.0, "speed": 0.0, "elapsed_ms": 212,
                        "provider": "network"},
    "termux-sensor": _demo_sensor,
    "termux-wifi-connectioninfo": {"bssid": "a4:2b:b0:1c:7e:f1", "frequency_mhz": 5180,
                                   "ip": "192.168.1.42", "link_speed_mbps": 433, "rssi": -54,
                                   "ssid": "HomeNet-5G", "ssid_hidden": False,
                                   "supplicant_state": "COMPLETED"},
    "termux-wifi-scaninfo": [
        {"ssid": "HomeNet-5G", "bssid": "a4:2b:b0:1c:7e:f1", "frequency_mhz": 5180, "rssi": -54},
        {"ssid": "HomeNet-2G", "bssid": "a4:2b:b0:1c:7e:f0", "frequency_mhz": 2437, "rssi": -61},
        {"ssid": "Voisin-Fibre", "bssid": "3c:97:0e:aa:12:90", "frequency_mhz": 2412, "rssi": -78},
        {"ssid": "CafeLibre", "bssid": "f4:ec:38:5d:00:21", "frequency_mhz": 5745, "rssi": -83}],
    "termux-telephony-deviceinfo": {"data_state": "connected", "phone_count": 2,
                                    "phone_type": "gsm", "network_operator_name": "Orange F",
                                    "network_country_iso": "fr", "network_type": "lte",
                                    "network_roaming": False, "sim_state": "ready"},
    "termux-telephony-cellinfo": [
        {"type": "lte", "registered": True, "dbm": -102, "level": 3, "mcc": 208, "mnc": 1},
        {"type": "lte", "registered": False, "dbm": -111, "level": 2, "mcc": 208, "mnc": 1}],
    "termux-sms-list": _demo_sms,
    "termux-contact-list": [
        {"name": "Maman", "number": "+33600000001"}, {"name": "Léa", "number": "+33600000002"},
        {"name": "Hugo", "number": "+33600000004"}, {"name": "Plombier", "number": "+33600000008"}],
    "termux-call-log": _demo_calls,
    "termux-clipboard-get": "https://github.com/termux/termux-api",
    "termux-volume": _demo_volume,
    "termux-notification-list": [
        {"id": 1, "packageName": "com.termux.api", "title": "Termux API Studio",
         "content": "Hello depuis le studio !"},
        {"id": 2, "packageName": "com.android.chrome", "title": "Téléchargement terminé",
         "content": "rapport.pdf"}],
    "termux-download": "Téléchargement ajouté à la file d'attente (démo).",
    "termux-job-scheduler": _demo_job,
    "termux-storage-list": [
        {"name": "Documents", "uri": "content://com.android.externalstorage.documents/tree/primary%3ADocuments"},
        {"name": "Download", "uri": "content://com.android.externalstorage.documents/tree/primary%3ADownload"}],
    "termux-tts-engines": [
        {"name": "com.google.android.tts", "label": "Synthèse vocale Google", "default": True},
        {"name": "com.samsung.SMT", "label": "Samsung TTS", "default": False}],
    "termux-media-player": _demo_player,
    "termux-media-scan": "Finished scanning 1 file(s) (démo).",
    "termux-microphone-record": _demo_record,
    "termux-dialog": _demo_dialog,
    "termux-audio-info": {"PROPERTY_OUTPUT_SAMPLE_RATE": "48000",
                          "PROPERTY_OUTPUT_FRAMES_PER_BUFFER": "192",
                          "BLUETOOTH_A2DP_IS_ON": False, "WIREDHEADSET_IS_CONNECTED": False},
    "termux-speech-to-text": "bonjour termux studio",
}


def get_demo(name: str, args: Optional[List[str]] = None) -> Any:
    """Valeur de démo d'une commande : dict/list (JSON), str (texte) ou None (aucune sortie)."""
    value = DEMO_DATA.get(name)
    if callable(value):
        value = value(args or [])  # type: ignore[misc]
    return value
