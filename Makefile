# Makefile

# Nom de l'environnement virtuel
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
DJANGO_MANAGE = $(PYTHON) manage.py

# Commandes
install:
	@echo "Création de l'environnement virtuel et installation des dépendances..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Installation terminée."

start:
	@echo "Démarrage du serveur Django..."
	$(DJANGO_MANAGE) runserver

test:
	@echo "Exécution des tests unitaires..."
	$(DJANGO_MANAGE) test

shell:
	@echo "Ouverture d'un shell interactif Django..."
	$(DJANGO_MANAGE) shell

migrate:
	@echo "Application des migrations..."
	$(DJANGO_MANAGE) migrate

migrations:
	@echo "Création des fichiers de migration..."
	$(DJANGO_MANAGE) makemigrations

help:
	@echo "Liste des commandes disponibles:"
	@echo "  make install     : Installe tous les requirements dans l'environnement virtuel"
	@echo "  make start       : Lance le serveur Django"
	@echo "  make test        : Exécute les tests unitaires"
	@echo "  make shell       : Accède au shell Django pour interagir avec la base de données"
	@echo "  make migrate     : Applique les migrations"
	@echo "  make migrations  : Crée les fichiers de migration"
	@echo "  make help        : Liste et explique les commandes disponibles"
