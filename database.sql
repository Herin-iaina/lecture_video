-- Schema de la base de donnees Lecture Video
-- Ce fichier est execute automatiquement par Docker au premier demarrage

-- Table des choix utilisateurs
CREATE TABLE IF NOT EXISTS user_choices (
    id SERIAL PRIMARY KEY,
    choix CHAR(1) NOT NULL,
    video TEXT NOT NULL,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    machine TEXT NOT NULL
);

-- Index pour les requetes frequentes
CREATE INDEX IF NOT EXISTS idx_user_choices_event_time ON user_choices(event_time);
CREATE INDEX IF NOT EXISTS idx_user_choices_machine ON user_choices(machine);
CREATE INDEX IF NOT EXISTS idx_user_choices_choix ON user_choices(choix);

-- Table des machines (bornes)
CREATE TABLE IF NOT EXISTS machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour la recherche par nom
CREATE INDEX IF NOT EXISTS idx_machines_name ON machines(name);
CREATE INDEX IF NOT EXISTS idx_machines_last_seen ON machines(last_seen);
