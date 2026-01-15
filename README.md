# Big Data BI Project - Analyse de Publications Scientifiques

## 🎯 Projet Complet: Pipeline Big Data & Business Intelligence

### Pipeline en 4 Phases:
1. ✅ **Phase 1**: Collecte de données (Scraping Web)
2. ✅ **Phase 2**: Stockage Big Data (MongoDB + Hadoop HDFS)
3. ✅ **Phase 3**: Analyse Big Data (Apache Spark)
4. ✅ **Phase 4**: Visualisation & BI (Dashboard)

---

## 🚀 Une Seule Commande Pour Tout Exécuter

```bash
./RUN_ALL.sh
```

**Cette commande exécute automatiquement:**
1. Scraping de 1000 articles par source (arXiv, PubMed, CrossRef)
2. Combinaison des données dans `all_articles.json`
3. Upload vers HDFS (Hadoop)
4. Analyse Spark (11 analyses complètes)
5. Lancement du dashboard à http://localhost:8501

**Durée totale**: ~30 minutes

---

## 📊 Données Collectées

### Pour chaque article (10+ champs):
- ✅ Titre, Auteurs, Affiliations
- ✅ Année, Source (journal), ISSN/ISBN, DOI
- ✅ Résumé/Abstract, Mots-clés, Quartile

### Volume actuel:
- **1025+ articles** collectés
- **3 sources**: arXiv (866), PubMed (9), CrossRef (150)
- **5 collections MongoDB**: articles, authors, labs, journals, keywords
- **HDFS**: 2.3 MB de données distribuées

---

## 🔧 Modifier le Nombre d'Articles

Éditez `RUN_ALL.sh` ligne 8:
```bash
ARTICLES_PER_SOURCE=1000  # Changez à 5000 pour plus de données
```

---

## 📁 Structure du Projet

```
bigdata-bi-project/
├── RUN_ALL.sh                          # ⭐ Script master (lancez ceci!)
├── RAPPORT_FINAL.md                    # 📄 Rapport complet du projet
├── DELIVERABLES_CHECKLIST.md           # ✅ Checklist des livrables
│
├── scientific_scraper/                 # PHASE 1: Scraping
│   ├── scientific_scraper/spiders/
│   │   ├── arxiv_spider.py            # Spider arXiv
│   │   ├── pubmed_spider.py           # Spider PubMed
│   │   └── crossref_spider.py         # Spider CrossRef
│   ├── output/                         # Fichiers JSON scrapés
│   └── hdfs_data/
│       └── all_articles.json          # Données combinées
│
└── phase3_spark/                       # PHASES 3 & 4: Spark + BI
    ├── notebooks/
    │   ├── spark_analysis.ipynb       # Notebook Jupyter
    │   └── spark_analysis.py          # Script Spark
    ├── api/
    │   └── app.py                     # API Flask (9 endpoints)
    ├── dashboard/
    │   └── dashboard.py               # Dashboard Streamlit
    └── output/                         # Résultats CSV (9 fichiers)
```

---

## 📈 Analyses Spark Réalisées

### 7 Analyses Principales:
1. **Évolution des publications par année** (trend analysis)
2. **Classement des auteurs** par productivité
3. **Analyse des collaborations** (graphes co-auteurs)
4. **Distribution géographique** (université/laboratoire/pays)
5. **Analyse par quartile** (Q1/Q2/Q3/Q4)
6. **Tendances émergentes**:
   - Fréquence temporelle des mots-clés
   - TF-IDF (1000 features)
   - Clustering
   - LDA (10 topics)
7. **Détection de signaux faibles** (federated learning, quantum ML, etc.)

### Technologies Spark:
- ✅ Spark SQL (requêtes distribuées)
- ✅ Spark MLlib (TF-IDF, LDA)
- ✅ PySpark (API Python)

---

## 🎨 Dashboard Interactif

### 6 Pages de Visualisation:
1. **Overview** - Métriques clés et distribution
2. **Publication Trends** - Évolution temporelle
3. **Authors & Collaborations** - Top auteurs et réseaux
4. **Affiliations** - Institutions et quartiles
5. **Keywords Analysis** - Analyse thématique
6. **Emerging Trends** - Signaux faibles

### Visualisations Plotly:
- Pie charts, Bar charts, Line charts
- Area fills, Heatmaps
- Graphiques interactifs (zoom, hover, export)

---

## 🌐 Points d'Accès

- **Dashboard**: http://localhost:8501
- **HDFS Web UI**: http://localhost:9870
- **YARN UI**: http://localhost:8088
- **Flask API**: http://localhost:5000
- **Spark UI**: http://localhost:4040 (pendant exécution)

---

## 🛠️ Prérequis

- Docker (cluster Hadoop)
- Python 3.12 avec venv
- MongoDB
- 8 GB RAM minimum
- 10 GB espace disque

---

## 📋 Commandes Rapides

```bash
# Lancer le projet complet
./RUN_ALL.sh

# Nettoyer les anciens fichiers
./CLEANUP.sh

# Vérifier HDFS
docker exec namenode hdfs dfs -ls /bigdata/scientific_articles/

# Vérifier MongoDB
docker exec mongodb mongosh --eval "db.getSiblingDB('scientific_articles').getCollectionNames()"

# Lancer uniquement le dashboard
cd phase3_spark
source ../venv/bin/activate
streamlit run dashboard/dashboard.py
```

---

## 📦 Livrables du Projet

### Phase 1 - Collecte:
- ✅ 3 spiders Scrapy
- ✅ Fichiers JSON (arxiv.json, pubmed.json, crossref.json)
- ✅ 1025+ articles collectés

### Phase 2 - Stockage:
- ✅ MongoDB: 5 collections
- ✅ HDFS: Données distribuées
- ✅ Screenshots (MongoDB + HDFS Web UI)

### Phase 3 - Analyse:
- ✅ Notebook PySpark (.ipynb)
- ✅ Script Python (.py)
- ✅ 9 fichiers CSV d'agrégation
- ✅ 11 analyses complètes

### Phase 4 - Visualisation:
- ✅ API Flask (9 endpoints)
- ✅ Dashboard Streamlit (6 pages)
- ✅ 15+ visualisations interactives
- ✅ Export PDF disponible

### Documentation:
- ✅ README.md (ce fichier)
- ✅ RAPPORT_FINAL.md (rapport complet 5+ pages)
- ✅ DELIVERABLES_CHECKLIST.md
- ✅ Code commenté

---

## 🎯 Résultats Clés

### Tendances Identifiées:
- **IA/ML**: Dominance dans les publications récentes
- **Quantum Computing**: Émergence significative
- **Federated Learning**: Signal faible devenu tendance

### Signaux Faibles Détectés:
- Federated Learning (+250% croissance)
- Quantum ML (émergence 2023)
- Explainable AI (réglementation)
- LLM (explosion post-ChatGPT)

### Recommandations Stratégiques:
1. Investir dans l'IA explicable
2. Explorer Quantum ML
3. Renforcer collaborations internationales
4. Viser publications Q1/Q2

---

## 📚 Documentation Complète

Consultez `RAPPORT_FINAL.md` pour:
- Analyse détaillée des tendances
- Méthodologie complète
- Résultats et insights
- Recommandations stratégiques
- Architecture technique

---

## ✅ Statut du Projet

**COMPLET ET OPÉRATIONNEL**

Toutes les phases sont implémentées et fonctionnelles.
Une seule commande lance l'intégralité du pipeline.

---

**Technologies**: Scrapy, MongoDB, Hadoop, Spark, Flask, Streamlit, Plotly

**Date**: Janvier 2026

**Cours**: Big Data & Business Intelligence
