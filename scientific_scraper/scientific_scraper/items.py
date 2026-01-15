import scrapy

class ScientificArticleItem(scrapy.Item):
    """
    Item pour stocker les informations d'un article scientifique
    """
    # Identifiants
    doi = scrapy.Field()
    article_id = scrapy.Field()
    source = scrapy.Field()  # arxiv, pubmed, core
    
    # Informations de base
    title = scrapy.Field()
    abstract = scrapy.Field()
    
    # Auteurs et affiliations
    authors = scrapy.Field()  # Liste d'auteurs
    affiliations = scrapy.Field()  # Liste d'affiliations
    
    # Publication
    journal = scrapy.Field()
    publisher = scrapy.Field()
    issn = scrapy.Field()
    isbn = scrapy.Field()
    
    # Dates
    date_published = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    
    # Catégorisation
    keywords = scrapy.Field()  # Liste de mots-clés
    subjects = scrapy.Field()  # Liste de sujets
    categories = scrapy.Field()  # Catégories spécifiques à la source
    
    # Métriques
    citations = scrapy.Field()
    views = scrapy.Field()
    
    # Qualité
    quartile = scrapy.Field()
    h_index = scrapy.Field()
    
    # Localisation
    country = scrapy.Field()
    university = scrapy.Field()
    laboratory = scrapy.Field()
    
    # Métadonnées
    url = scrapy.Field()
    pdf_url = scrapy.Field()
    language = scrapy.Field()
    
    # Timestamp
    scraped_at = scrapy.Field()
