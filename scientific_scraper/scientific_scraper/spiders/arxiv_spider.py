import scrapy
import xmltodict
from datetime import datetime
from scientific_scraper.items import ScientificArticleItem

class ArxivSpider(scrapy.Spider):
    name = 'arxiv'
    allowed_domains = ['export.arxiv.org']
    
    # Sujets liés au projet
    search_queries = [
        'machine learning',
        'blockchain',
        'big data',
        'deep learning',
        'artificial intelligence',
        'data mining'
    ]
    
    def __init__(self, keywords=None, max_results=100, *args, **kwargs):
        super(ArxivSpider, self).__init__(*args, **kwargs)
        
        if keywords:
            self.search_queries = [keywords]
        
        self.max_results = max_results
        self.base_url = 'http://export.arxiv.org/api/query'
    
    def start_requests(self):
        """
        Génère les requêtes pour chaque sujet de recherche
        """
        for query in self.search_queries:
            # Construction de l'URL de recherche
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': self.max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            url = f"{self.base_url}?search_query=all:{query.replace(' ', '+')}&start=0&max_results={self.max_results}&sortBy=submittedDate&sortOrder=descending"
            
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'query': query}
            )
    
    def parse(self, response):
        """
        Parse la réponse XML de l'API arXiv
        """
        # Parser le XML
        data = xmltodict.parse(response.text)
        
        # Extraire les entrées
        entries = data.get('feed', {}).get('entry', [])
        
        # Si une seule entrée, la convertir en liste
        if isinstance(entries, dict):
            entries = [entries]
        
        for entry in entries:
            item = ScientificArticleItem()
            
            # ID et source
            arxiv_id = entry.get('id', '').split('/abs/')[-1]
            item['article_id'] = arxiv_id
            item['source'] = 'arxiv'
            item['doi'] = entry.get('arxiv:doi', {}).get('#text', '') if isinstance(entry.get('arxiv:doi'), dict) else entry.get('arxiv:doi', '')
            
            # Informations de base
            item['title'] = entry.get('title', '').replace('\n', ' ').strip()
            item['abstract'] = entry.get('summary', '').replace('\n', ' ').strip()
            
            # Auteurs
            authors = entry.get('author', [])
            if isinstance(authors, dict):
                authors = [authors]
            
            item['authors'] = [
                author.get('name', '') for author in authors
            ]
            
            # Affiliations (pas toujours disponibles dans arXiv)
            item['affiliations'] = []
            
            # Date de publication
            published = entry.get('published', '')
            if published:
                try:
                    pub_date = datetime.strptime(published[:10], '%Y-%m-%d')
                    item['date_published'] = published[:10]
                    item['year'] = pub_date.year
                    item['month'] = pub_date.month
                except:
                    item['date_published'] = published
                    item['year'] = None
                    item['month'] = None
            
            # Catégories
            categories = entry.get('category', [])
            if isinstance(categories, dict):
                categories = [categories]
            
            item['categories'] = [
                cat.get('@term', '') for cat in categories
            ]
            item['subjects'] = item['categories']
            
            # Mots-clés (extraction depuis le résumé ou titre)
            item['keywords'] = [response.meta['query']]
            
            # URLs
            item['url'] = entry.get('id', '')
            
            # PDF URL
            links = entry.get('link', [])
            if isinstance(links, dict):
                links = [links]
            
            for link in links:
                if link.get('@title') == 'pdf':
                    item['pdf_url'] = link.get('@href', '')
                    break
            
            # Journal (arXiv n'a pas de journal traditionnel)
            item['journal'] = 'arXiv preprint'
            item['publisher'] = 'arXiv'
            
            # Métadonnées
            item['language'] = 'en'
            item['scraped_at'] = datetime.now().isoformat()
            
            # Champs optionnels
            item['citations'] = None
            item['views'] = None
            item['quartile'] = None
            item['h_index'] = None
            item['country'] = None
            item['university'] = None
            item['laboratory'] = None
            item['issn'] = None
            item['isbn'] = None
            
            yield item
