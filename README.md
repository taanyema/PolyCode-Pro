# Chatbot IA Web

## Description
Un chatbot simple avec interface web pour discuter avec une IA, idéal pour débutants.  
Le projet utilise **Python** et **Flask** pour le serveur et **GPT-5 via Replit AI** pour l’intelligence artificielle.  
L’interface web est simple et permet de discuter comme dans une application de messagerie classique.

## Fonctionnalités
- Discussion avec l’IA en temps réel
- Interface web simple et élégante
- Personnalisation facile (messages et style)

## Prérequis
- Python (géré par Replit)
- Flask (installé automatiquement par Replit)
- Accès à Replit AI (déjà configuré)

## Installation
> Tout est configuré automatiquement par Replit, aucune installation manuelle nécessaire.  
> Pour exécuter le chatbot, il suffit de cliquer sur **Run**.

## Utilisation
1. Cliquer sur **Run** dans l’éditeur Replit
2. Ouvrir la **Webview** (prévisualisation)
3. Taper un message dans la zone de texte et appuyer sur **Entrée** ou **Envoyer**
4. Le chatbot répond instantanément

## Configuration (variables d’environnement)
- Aucune clé API requise, tout est déjà configuré pour utiliser GPT-5 via Replit

## Architecture du projet
- `main.py` : serveur Flask + logique du chatbot
- `templates/index.html` : interface web (HTML/CSS/JS)
- `README.md` : documentation
- `requirements.txt` : dépendances Python (gérées par Replit)
- Flux : Frontend → Flask → GPT-5 → Frontend

## Déploiement
- Méthode : Cloud Replit
- URL fournie automatiquement (ex : infatuated-dazzling-jumpthreading--soamboalacoulid.replit.app)

## Personnalisation
- Changer la personnalité ou le comportement du chatbot → modifier `main.py`
- Changer le style / couleurs → modifier `templates/index.html`

## Licence
- MIT License  
- © 2026 Soamboala Coulidiati

## Crédits
- Replit pour l’environnement et l’IA intégrée
- GPT-5 pour la génération de réponses