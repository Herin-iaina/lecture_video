# Video Analytics Dashboard

Dashboard React pour visualiser les donnees des bornes video.

## Fonctionnalites

- Filtrage par machine et periode
- Cartes de statistiques en temps reel
- Graphiques interactifs (barres, camembert, ligne)
- Tableau de donnees triable
- Export en XLSX et CSV

## Installation

```bash
# Installer les dependances
npm install

# Lancer en developpement
npm run dev

# Build pour la production
npm run build
```

## Developpement

Le serveur de developpement tourne sur `http://localhost:3000`.

Un proxy est configure pour rediriger `/api` vers `http://localhost:8000` (le serveur FastAPI).

## Production

```bash
# Build
npm run build

# Les fichiers sont generes dans dist/
```

Pour servir le dashboard en production, vous pouvez:

1. **Option 1**: Servir les fichiers statiques avec Nginx
2. **Option 2**: Integrer dans FastAPI (voir ci-dessous)

### Integration avec FastAPI

Ajoutez dans `server/main.py`:

```python
from fastapi.staticfiles import StaticFiles

# Apres la creation de l'app
app.mount("/", StaticFiles(directory="../dashboard/dist", html=True), name="static")
```

## Technologies

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Recharts (graphiques)
- xlsx (export)
