# Dockerfile pour le dashboard React
# Build multi-stage: Node pour le build, Nginx pour servir

# === Stage 1: Build ===
FROM node:20-alpine AS builder

WORKDIR /app

# Copie des fichiers de dependances
COPY package.json package-lock.json* ./

# Installation des dependances
RUN npm ci

# Copie du code source
COPY . .

# Build de l'application
RUN npm run build

# === Stage 2: Production ===
FROM nginx:alpine

# Copie de la configuration Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers buildés
COPY --from=builder /app/dist /usr/share/nginx/html

# Port expose
EXPOSE 80

# Commande de demarrage
CMD ["nginx", "-g", "daemon off;"]
