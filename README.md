# VideoMPMLinux

Systeme de lecture video interactif pour bornes/kiosques avec architecture client-serveur.

## Architecture

```
┌─────────────┐     Serie     ┌─────────────┐     HTTP      ┌─────────────┐
│   Arduino   │ ───────────── │   Client    │ ───────────── │   Serveur   │
│  (Boutons)  │               │   (Borne)   │               │   (API)     │
└─────────────┘               └──────┬──────┘               └──────┬──────┘
                                     │                             │
                                     ▼                             ▼
                              ┌─────────────┐               ┌─────────────┐
                              │    Ecran    │               │ PostgreSQL  │
                              │   (Video)   │               │ (Analytics) │
                              └─────────────┘               └─────────────┘

        ┌─────────────┐
        │   Client    │──────┐
        │  (Borne 2)  │      │
        └─────────────┘      │
                             ├──────▶ Serveur API (centralise)
        ┌─────────────┐      │
        │   Client    │──────┘
        │  (Borne N)  │
        └─────────────┘
```

## Avantages

- **Centralisation** : Toutes les donnees sur un seul serveur
- **Simplicite** : Les bornes n'ont pas besoin de PostgreSQL
- **Evolutivite** : Ajoutez des bornes facilement
- **Analyses globales** : Dashboard unifie pour toutes les bornes

## Structure du projet

```
videoMPMLinux/
├── server/                 # API centralisee
│   ├── main.py            # Application FastAPI
│   ├── models.py          # Modeles SQLAlchemy
│   ├── schemas.py         # Schemas Pydantic
│   ├── database.py        # Connexion PostgreSQL
│   ├── requirements.txt   # Dependances serveur
│   └── .env.example       # Configuration serveur
│
├── client/                 # Client video (borne)
│   ├── main.py            # Application principale
│   ├── config.py          # Configuration
│   ├── api_client.py      # Client HTTP
│   ├── requirements.txt   # Dependances client
│   └── .env.example       # Configuration client
│
├── dashboard/              # Interface web React
│   ├── src/               # Code source
│   ├── package.json       # Dependances npm
│   └── README.md          # Documentation
│
├── main.cpp               # Firmware Arduino
├── database.sql           # Schema initial
└── service.ini            # Service SystemD (client)
```

## Installation

### Serveur (1 seul pour toutes les bornes)

```bash
cd server/

# Dependances
pip install -r requirements.txt

# Configuration
cp .env.example .env
nano .env  # Modifier DB_PASSWORD

# Base de donnees
sudo -u postgres psql -f ../database.sql

# Lancer
python main.py
# ou en production:
uvicorn main:app --host 0.0.0.0 --port 8000
```

L'API est accessible sur `http://server-ip:8000`
- Documentation Swagger: `http://server-ip:8000/docs`
- Documentation ReDoc: `http://server-ip:8000/redoc`

### Client (sur chaque borne)

```bash
cd client/

# Dependances systeme
sudo apt install python3 python3-pip mpv

# Dependances Python
pip install -r requirements.txt

# Configuration
cp .env.example .env
nano .env  # Modifier API_URL et MACHINE_NAME

# Structure des videos
mkdir -p videos/{A,B,C,D,E,F,G}
# Placer generic.mp4 dans videos/
# Placer les videos dans les sous-dossiers A-G

# Lancer
python main.py
```

### Dashboard (interface web)

```bash
cd dashboard/

# Installer les dependances
npm install

# Lancer en developpement
npm run dev
# Accessible sur http://localhost:3000

# Build pour production
npm run build
```

**Fonctionnalites:**
- Filtrage par machine et periode
- Graphiques interactifs (barres, camembert, courbe)
- Tableau de donnees triable
- Export XLSX et CSV

### Arduino

Flasher `main.cpp` sur l'Arduino.

| Bouton | Pin |
|--------|-----|
| A | 2 |
| B | 3 |
| C | 4 |
| D | 5 |
| E | 6 |
| F | 7 |
| G | 8 |

## API Endpoints

### Choices

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/choices` | Enregistrer un choix |
| GET | `/choices` | Lister les choix |
| GET | `/choices/{id}` | Recuperer un choix |
| DELETE | `/choices/{id}` | Supprimer un choix |

### Machines

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/machines` | Enregistrer une machine |
| GET | `/machines` | Lister les machines |
| GET | `/machines/{name}` | Recuperer une machine |
| PUT | `/machines/{name}` | Mettre a jour |
| DELETE | `/machines/{name}` | Supprimer |

### Statistics

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/stats` | Statistiques globales |
| GET | `/stats/live` | Temps reel |
| GET | `/health` | Etat du serveur |

## Deploiement Docker

### Production (recommande)

```bash
# Configurer les variables d'environnement
cp .env.example .env
nano .env  # Modifier DB_PASSWORD

# Lancer tous les services
docker-compose up -d

# Verifier les logs
docker-compose logs -f
```

Services disponibles:
- **Dashboard**: http://localhost:8080
- **API**: http://localhost:8001
- **PostgreSQL**: localhost:5433

### Developpement (avec hot-reload)

```bash
docker-compose -f docker-compose.dev.yml up
```

Services en mode dev:
- **Dashboard**: http://localhost:3000 (hot-reload)
- **API**: http://localhost:8001 (hot-reload)
- **PostgreSQL**: localhost:5433

### Commandes utiles

```bash
# Arreter les services
docker-compose down

# Rebuild les images
docker-compose build --no-cache

# Voir les logs d'un service
docker-compose logs -f api

# Supprimer les volumes (reset DB)
docker-compose down -v
```

## Deploiement production (sans Docker)

### Serveur (SystemD)

```bash
sudo mkdir -p /opt/video_api
sudo cp server/* /opt/video_api/

sudo tee /etc/systemd/system/video-api.service << EOF
[Unit]
Description=Video Analytics API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/video_api
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now video-api
```

### Client (SystemD)

```bash
sudo mkdir -p /opt/video_player
sudo cp client/* /opt/video_player/
sudo useradd -r -s /bin/false video
sudo chown -R video:video /opt/video_player
sudo cp service.ini /etc/systemd/system/video-player.service
sudo systemctl enable --now video-player
```

## Configuration

### Serveur

| Variable | Description | Defaut |
|----------|-------------|--------|
| `API_HOST` | Interface | `0.0.0.0` |
| `API_PORT` | Port | `8000` |
| `DB_HOST` | Hote PostgreSQL | `localhost` |
| `DB_NAME` | Base | `video_analytics` |
| `DB_PASSWORD` | Mot de passe | (requis) |

### Client

| Variable | Description | Defaut |
|----------|-------------|--------|
| `SERIAL_PORT` | Port serie | `/dev/ttyUSB0` |
| `VIDEO_ROOT` | Dossier videos | `./videos` |
| `API_URL` | URL serveur | `http://localhost:8000` |
| `MACHINE_NAME` | Nom borne | `borne_01` |
| `MACHINE_LOCATION` | Emplacement | (optionnel) |

## Exemples API

```bash
# Enregistrer un choix
curl -X POST http://server:8000/choices \
  -H "Content-Type: application/json" \
  -d '{"choix": "A", "video": "/videos/A/demo.mp4", "machine": "borne_01"}'

# Statistiques
curl http://server:8000/stats?days=7

# Machines actives
curl http://server:8000/machines
```

## Formats video

MP4, MKV, AVI, MOV, WebM

## License

MIT
