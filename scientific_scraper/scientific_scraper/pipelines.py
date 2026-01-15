import pymongo
from datetime import datetime
import logging

class MongoDBPipeline:
    """
    Pipeline pour sauvegarder les items dans MongoDB
    """
    
    collection_name = 'articles'
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
        
    @classmethod
    def from_crawler(cls, crawler):
        """
        Récupère la configuration depuis settings.py
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'scientific_articles')
        )
    
    def open_spider(self, spider):
        """
        Appelé quand le spider démarre
        """
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            
            # Créer des index pour améliorer les performances
            self.db[self.collection_name].create_index([('article_id', pymongo.ASCENDING)])
            self.db[self.collection_name].create_index([('doi', pymongo.ASCENDING)])
            self.db[self.collection_name].create_index([('source', pymongo.ASCENDING)])
            self.db[self.collection_name].create_index([('year', pymongo.DESCENDING)])
            self.db[self.collection_name].create_index([('date_published', pymongo.DESCENDING)])
            
            # Index texte pour la recherche full-text
            self.db[self.collection_name].create_index([
                ('title', 'text'),
                ('abstract', 'text'),
                ('keywords', 'text')
            ])
            
            spider.logger.info(f"Connected to MongoDB: {self.mongo_db}")
            
        except Exception as e:
            spider.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def close_spider(self, spider):
        """
        Appelé quand le spider se termine
        """
        if self.client:
            self.client.close()
            spider.logger.info("MongoDB connection closed")
    
    def process_item(self, item, spider):
        """
        Traite chaque item et le sauvegarde dans MongoDB
        """
        try:
            # Convertir l'item en dictionnaire
            item_dict = dict(item)
            
            # Vérifier si l'article existe déjà (éviter les doublons)
            existing = None
            
            if item_dict.get('doi'):
                existing = self.db[self.collection_name].find_one({'doi': item_dict['doi']})
            
            if not existing and item_dict.get('article_id'):
                existing = self.db[self.collection_name].find_one({
                    'article_id': item_dict['article_id'],
                    'source': item_dict['source']
                })
            
            if existing:
                # Mettre à jour l'article existant
                self.db[self.collection_name].update_one(
                    {'_id': existing['_id']},
                    {'$set': item_dict}
                )
                spider.logger.debug(f"Updated existing article: {item_dict.get('title', 'Unknown')}")
            else:
                # Insérer un nouvel article
                self.db[self.collection_name].insert_one(item_dict)
                spider.logger.debug(f"Inserted new article: {item_dict.get('title', 'Unknown')}")
            
            return item
            
        except Exception as e:
            spider.logger.error(f"Error processing item: {e}")
            spider.logger.error(f"Item: {item}")
            raise


class DataCleaningPipeline:
    """
    Pipeline pour nettoyer les données avant stockage
    """
    
    def process_item(self, item, spider):
        """
        Nettoie et normalise les données
        """
        # Nettoyer le titre
        if item.get('title'):
            item['title'] = ' '.join(item['title'].split())
            item['title'] = item['title'].strip()
        
        # Nettoyer l'abstract
        if item.get('abstract'):
            item['abstract'] = ' '.join(item['abstract'].split())
            item['abstract'] = item['abstract'].strip()
        
        # Normaliser les auteurs
        if item.get('authors'):
            item['authors'] = [author.strip() for author in item['authors'] if author.strip()]
        
        # Normaliser les mots-clés
        if item.get('keywords'):
            # Convertir en minuscules et supprimer les doublons
            keywords = [kw.lower().strip() for kw in item['keywords'] if kw]
            item['keywords'] = list(set(keywords))
        
        # Valider l'année
        if item.get('year'):
            try:
                year = int(item['year'])
                if year < 1900 or year > datetime.now().year + 1:
                    item['year'] = None
            except:
                item['year'] = None
        
        # Valider le mois
        if item.get('month'):
            try:
                month = int(item['month'])
                if month < 1 or month > 12:
                    item['month'] = None
            except:
                item['month'] = None
        
        return item


class DuplicateFilterPipeline:
    """
    Pipeline pour filtrer les doublons basés sur DOI ou titre
    """
    
    def __init__(self):
        self.seen_dois = set()
        self.seen_titles = set()
    
    def process_item(self, item, spider):
        """
        Vérifie si l'item est un doublon
        """
        # Vérifier par DOI
        if item.get('doi'):
            if item['doi'] in self.seen_dois:
                spider.logger.debug(f"Duplicate DOI found: {item['doi']}")
                raise DropItem(f"Duplicate DOI: {item['doi']}")
            self.seen_dois.add(item['doi'])
        
        # Vérifier par titre (normalisation)
        if item.get('title'):
            normalized_title = item['title'].lower().strip()
            if normalized_title in self.seen_titles:
                spider.logger.debug(f"Duplicate title found: {item['title']}")
                # Ne pas lever DropItem pour les titres, car ils peuvent être légitimes
                # raise DropItem(f"Duplicate title: {item['title']}")
            self.seen_titles.add(normalized_title)
        
        return item


from scrapy.exceptions import DropItem
