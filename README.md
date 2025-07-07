# 1-scraping-data — Version 1.0.0

## Description

Automatisation complète du scraping des conventions collectives et des Bulletins Officiels des Conventions Collectives (BOCC) sur Legifrance, incluant : extraction, structuration, téléchargement, gestion robuste des fichiers, logs, relances intelligentes, et interface CLI conviviale.  
Ce module constitue la base de données documentaire pour l’indexation et l’amélioration des réponses d’un LLM (RAG).

---

## 🗂️ Architecture du projet

```bash
.
├── data
│   ├── code_du_travail
│   └── conventions_etendues
├── logs
│   ├── bocc
│   └── convention_etendues
├── main.py
├── pyproject.toml
├── README.md
├── releases.md
├── src
│   ├── links_preprocessing.py
│   ├── links_scraping_BOCC.py
│   ├── links_scraping_conventions_etendues.py
│   ├── no_pdf_bocc.py
│   ├── no_pdf_conventions_etendues_download.py
│   ├── pdf_bocc.py
│   ├── pdf_conventions_etendues_download.py
│   ├── __pycache__
│   └── utils.py
├── todo.md
└── uv.lock
```

---

## 📥 Cloner le dépôt

```bash
git clone https://github.com/Malek-Boumedine/LLM_data_scraping.git
cd LLM_data_scraping/1.Scraping_data
```

---

## ⚡ Installation des dépendances

Assurez-vous d’avoir **Python ≥ 3.11** et [uv](https://github.com/astral-sh/uv) installé.

```bash
uv pip install
```

---

## 🚀 Utilisation

Lancez simplement :

```bash
python main.py
```

Le menu interactif s’affichera :  
- Suivez les instructions à l’écran pour choisir l’action désirée (scraping, téléchargement, logs…)
- Les données, PDF et logs seront enregistrés automatiquement dans les dossiers prévus (`data/`, `logs/`).

---

## 🚀 Fonctionnalités principales

- **Scraping automatique** de Legifrance pour les conventions étendues et BOCC
- **Extraction, nettoyage et sauvegarde structurée** des données en JSON
- **Téléchargement, fusion et vérification des fichiers PDF** collectés
- **Interface interactive en ligne de commande** (CLI) avec menus, confirmations et navigation intuitive
- **Gestion robuste des dossiers et fichiers** (création automatique, protection contre les erreurs de fichiers vides/corrompus, suppression intelligente)
- **Logs détaillés** pour chaque étape du process (scraping, erreurs, téléchargements)
- **Prétraitement et relance automatique** sur échecs (multi-tentatives, vérification d’existants)
- **Vérification de la validité des PDF** (intégrité, possibilité de suppression automatique des corrompus)
- **Prise en charge du “premier lancement”** : aucune action manuelle ou redémarrage requis après extraction initiale
- **Compatible Windows, Linux, macOS** (testé avec Python 3.11+ et `uv`)

---

## 🛠️ Bibliothèques principales

| Bibliothèque         | Version requise    | Badge                                                                                  | Rôle principal                      |
|--------------------- |-------------------|----------------------------------------------------------------------------------------|-------------------------------------|
| Playwright           | `>=1.53.0`        | ![Playwright](https://img.shields.io/badge/Playwright-2D2D2D?style=flat-square&logo=microsoft&logoColor=white) | Scraping headless (JS, anti-bot)    |
| cloudscraper         | `>=1.2.71`        | ![Cloudscraper](https://img.shields.io/badge/cloudscraper-20232A?style=flat-square&logo=cloudflare&logoColor=orange) | Bypass protections anti-bot         |
| PyPDF2               | `>=3.0.1`         | ![PyPDF2](https://img.shields.io/badge/PyPDF2-3776AB?style=flat-square&logo=python&logoColor=white) | Manipulation/merge PDF              |
| python-dotenv        | `>=0.9.9`         | ![Dotenv](https://img.shields.io/badge/dotenv-55A8FD?style=flat-square&logo=python&logoColor=white) | Gestion de la configuration         |
| uv                   | `latest`          | ![uv](https://img.shields.io/badge/uv-3C5CBC?style=flat-square&logo=python&logoColor=white) | Gestion rapide des dépendances      |

---

## 🔑 Autres points clés

- **Structure des dossiers claire** : `data/`, `logs/`, `src/`, etc.
- **Fonctions utilitaires** pour la gestion et la vérification des fichiers (création, suppression, validation PDF)
- **Simplicité d’installation** : compatible pip/uv, instructions dans le README
- **Licence MIT**, contributions bienvenues !

---

## 🚩 Prérequis

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) ou `pip` pour l’installation rapide des dépendances

---

**N’hésitez pas à ouvrir une issue ou une PR pour contribuer ou signaler un bug !**
