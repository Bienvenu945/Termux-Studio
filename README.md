# ⚡ Termux API Studio

```
[ Python 3.9+ ]  [ Rich TUI ]  [ Termux ✓ ]  [ Linux ✓ ]  [ MIT ]  [ 40 commandes ]
```

> Pilote ton Android depuis le terminal — termux-api, version badass.

Un studio interactif en ligne de commande (TUI) pour **explorer, exécuter et visualiser**
les commandes `termux-*` du paquet `termux-api` : panneaux stylés, header ASCII en dégradé,
JSON coloré, tables automatiques, jauges, spinners et thèmes. Une seule dépendance : [Rich](https://github.com/Textualize/rich).

## 🖼 Aperçu

Menu principal (`python main.py --demo`, capture sans couleurs) :

```
            ████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗
            ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║╚██╗██╔╝
               ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║ ╚███╔╝
               ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║ ██╔██╗
               ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗
               ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
                ███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗
                ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗
                ███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║
                ╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║
                ███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝
                ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝
             ⚡ termux-api · explorer · exécuter · visualiser ⚡
╔═════════════════════════  ✦ TERMUX API STUDIO ✦  ══════════════════════════╗
║                         Termux API Studio  v1.0.0                          ║
║    Pilote ton Android depuis le terminal — termux-api, version badass.     ║
╚════════════════  🖥  Desktop · 🐍 Python 3.12.3  MODE DÉMO  ════════════════╝
╭─────────────────────────────  Menu principal  ─────────────────────────────╮
│                                                                            │
│  [1] 🔧  Matériel           Batterie, caméra, GPS, capteurs, Wi-Fi,        │
│                             téléphonie (13)                                │
│  [2] 💬  Communication      SMS, contacts, journal d'appels, appels (5)    │
│  [3] 🧩  Système            Presse-papier, notifications, volume,          │
│                             téléchargements (14)                           │
│  [4] 🎵  Média              Voix, lecteur audio, micro, dialogues, fond    │
│                             d'écran (10)                                   │
│                                                                            │
│  [5] ★  Favoris             0 commande(s) épinglée(s)                      │
│  [6] 🔎 Rechercher          Filtrer par nom ou description                 │
│  [7] ℹ  Infos               Environnement, version, chemins                │
│                                                                            │
│  [q] ✗  Quitter                                                            │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
──────────────────────────────────────────────────────────────────────────────
   💡 Astuce : termux-sms-send nécessite la permission SMS pour Termux:API.
```

Résultat d'une commande (`python main.py --demo --run termux-battery-status`) :

```
╭─────────────────────────  termux-battery-status  ──────────────────────────╮
│ {                                                                          │
│   "health": "GOOD",                                                        │
│   "percentage": 87,                                                        │
│   "plugged": "UNPLUGGED",                                                  │
│   "status": "DISCHARGING",                                                 │
│   "temperature": 29.4,                                                     │
│   "current": -412000                                                       │
│ }                                                                          │
╰─────────────────────────────  ⏱ 300 ms  DÉMO  ─────────────────────────────╯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 📦 Installation

### Termux (Android)

```bash
pkg install -y python termux-api
pip install -r requirements.txt
python main.py
```

Ou tout d'un coup : `bash install.sh`.
Installe aussi l'application **Termux:API** (voir *Prérequis*).

### Desktop (Linux / macOS)

```bash
bash install.sh                 # pip, ou un venv .venv si pip refuse (PEP 668)
python3 main.py --demo          # les commandes termux-* n'existent pas hors Android
```

Sans Termux, le studio reste utilisable : le **mode démo** (`--demo`) simule toutes les commandes
avec des données fictives réalistes.

## 🚀 Utilisation

### TUI interactif

```bash
python main.py                      # menu complet
python main.py --demo               # données fictives (aucune commande exécutée)
python main.py --theme magenta      # palettes : cyan (défaut) | magenta | mono
python main.py --category hardware  # ouvre directement une catégorie
```

Navigation : tape le numéro de l'entrée puis Entrée. `0` = retour, `q` = quitter.
**Ctrl+C** ramène au menu précédent sans quitter (au menu principal, une confirmation est demandée).
Après chaque commande : relancer, modifier les paramètres, basculer table ↔ JSON, ajouter aux favoris.

### CLI direct

```bash
python main.py --version
python main.py --check                                  # état de l'environnement
python main.py --run termux-battery-status
python main.py --run battery-status                     # le préfixe termux- est facultatif
python main.py --run termux-sms-list -l 5 -t inbox      # tout ce qui suit --run est transmis
python main.py --demo --run termux-sms-list -l 3        # place --demo/--theme AVANT --run
```

`--run` retourne le code `0` si la commande a réussi, `1` sinon.
`--check` retourne toujours `0` : il affiche simplement l'état (même hors Termux).

### Favoris

```bash
python main.py --fav add termux-torch
python main.py --fav list
python main.py --fav remove termux-torch
```

Stockés dans `~/.termux-studio/favorites.json` et disponibles dans le menu **★ Favoris**.

## 📋 Commandes supportées (40)

### 🔧 Matériel (`--category hardware`)

| Commande | Description | Permission Android |
|---|---|---|
| `termux-battery-status` | État de la batterie (niveau, température, santé) | — |
| `termux-camera-info` | Informations sur les caméras (id, orientation, résolutions) | Caméra |
| `termux-camera-photo` | Prend une photo avec la caméra choisie *(aussi dans Média)* | Caméra |
| `termux-fingerprint` | Authentification par empreinte digitale | Biométrie |
| `termux-location` | Position GPS / réseau (latitude, longitude, précision) | Localisation |
| `termux-sensor` | Lit les capteurs du téléphone (accéléromètre, gyroscope…) | — |
| `termux-torch` | Allume / éteint la lampe torche | Caméra |
| `termux-vibrate` | Fait vibrer le téléphone | — |
| `termux-wifi-connectioninfo` | Infos sur la connexion Wi-Fi actuelle (SSID, IP, signal) | — |
| `termux-wifi-scaninfo` | Scan des réseaux Wi-Fi alentour | Localisation |
| `termux-wifi-enable` | Active ou désactive le Wi-Fi *(aussi dans Système)* | — |
| `termux-telephony-deviceinfo` | Infos téléphonie : opérateur, réseau, état de la SIM | Téléphone |
| `termux-telephony-cellinfo` | Infos sur les antennes-relais (cellules) visibles | Téléphone / Localisation |

### 💬 Communication (`--category communication`)

| Commande | Description | Permission Android |
|---|---|---|
| `termux-sms-list` | Liste les SMS (inbox, envoyés, brouillons…) | SMS |
| `termux-sms-send` | Envoie un SMS | SMS |
| `termux-contact-list` | Liste les contacts du téléphone | Contacts |
| `termux-call-log` | Journal d'appels récent | Journal d'appels |
| `termux-telephony-call` | Passe un appel téléphonique | Téléphone |

### 🧩 Système (`--category system`)

| Commande | Description | Permission Android |
|---|---|---|
| `termux-clipboard-get` | Lit le contenu du presse-papier | — |
| `termux-clipboard-set` | Écrit du texte dans le presse-papier | — |
| `termux-notification` | Affiche une notification Android | — |
| `termux-notification-remove` | Retire une notification par son identifiant | — |
| `termux-notification-list` | Liste les notifications actives | Accès aux notifications |
| `termux-toast` | Affiche un toast (message flottant) | — |
| `termux-volume` | Affiche ou règle les volumes audio | — |
| `termux-brightness` | Règle la luminosité de l'écran (0-255 ou auto) | Modifier les paramètres système |
| `termux-download` | Télécharge un fichier via le gestionnaire Android | Stockage |
| `termux-job-scheduler` | Planifie un script périodique (JobScheduler Android) | — |
| `termux-share` | Partage un fichier via le menu de partage Android | — |
| `termux-storage-get` | Ouvre le sélecteur de fichiers Android et copie le choix | — |
| `termux-storage-list` | Liste les dossiers de stockage autorisés (SAF, via termux-saf-dirs) | — |
| `termux-wifi-enable` | Active ou désactive le Wi-Fi *(partagée)* | — |

### 🎵 Média (`--category media`)

| Commande | Description | Permission Android |
|---|---|---|
| `termux-tts-speak` | Synthèse vocale : lit un texte à voix haute | — |
| `termux-tts-engines` | Liste les moteurs de synthèse vocale installés | — |
| `termux-media-player` | Contrôle le lecteur audio (info, play, pause, stop) | — |
| `termux-media-scan` | Demande à Android de (ré)indexer des fichiers média | Stockage |
| `termux-microphone-record` | Enregistre le micro (ou affiche / stoppe l'enregistrement) | Micro |
| `termux-dialog` | Boîtes de dialogue Android (texte, confirmation, liste…) | — |
| `termux-wallpaper` | Change le fond d'écran (fichier ou URL) | — |
| `termux-audio-info` | Infos sur le sous-système audio du téléphone | — |
| `termux-speech-to-text` | Reconnaissance vocale : transcrit ce que tu dis | Micro |
| `termux-camera-photo` | Prend une photo avec la caméra choisie *(partagée)* | Caméra |

> **Note** : `termux-storage-list` n'existe pas dans `termux-api`. Le studio l'exécute via
> `termux-saf-dirs` (liste des dossiers autorisés via le Storage Access Framework).
> `termux-wifi-enable` et `termux-camera-photo` apparaissent dans deux catégories.

## ✅ Prérequis

1. **Termux** (de préférence depuis [F-Droid](https://f-droid.org/packages/com.termux/)).
2. Le paquet : `pkg install termux-api`.
3. L'**application Termux:API** depuis [F-Droid](https://f-droid.org/packages/com.termux.api/)
   (même source que Termux, sinon les signatures ne correspondent pas).
4. Les **permissions Android** de l'app Termux:API (Réglages → Applications → Termux:API → Autorisations) :
   SMS, Contacts, Journal d'appels, Téléphone, Localisation, Caméra, Micro, Stockage selon les commandes utilisées.
5. Pour la lampe torche, la luminosité ou le fond d'écran, certains réglages système peuvent demander une autorisation supplémentaire.
6. `termux-setup-storage` pour accéder à `/sdcard` depuis Termux.

Si une commande se fige ou expire, c'est presque toujours une permission refusée ou l'app Termux:API absente.

## 🗂 Structure

```
termux-studio/
├── main.py            # point d'entrée (argparse)
├── config.py          # constantes, thèmes, environnement, favoris
├── catalog.py         # catalogue des commandes + données de démo
├── runner.py          # exécution subprocess (sans shell) + parsing JSON
├── ui.py              # helpers Rich (header, panels, tables, invites)
├── views/             # menu principal + 4 catégories
├── requirements.txt
├── install.sh
└── LICENSE
```

## 🔒 Sécurité et vie privée

- Aucune commande n'est lancée via un shell : les arguments sont passés tels quels à `subprocess`.
- Seuls les noms `termux-*` sont acceptés.
- `termux-sms-send` et `termux-telephony-call` demandent une confirmation explicite.
- Le dernier appel (commande, durée, sortie) est écrit dans `~/.termux-studio/last_run.log`
  (droits `600`). La sortie peut contenir des données personnelles (SMS, contacts…) :
  définis `TERMUX_STUDIO_NOLOG=1` pour désactiver ce log.
- `TERMUX_STUDIO_DEBUG=1` affiche la trace complète en cas d'erreur inattendue.

## 📄 Licence

MIT — voir [LICENSE](LICENSE).
