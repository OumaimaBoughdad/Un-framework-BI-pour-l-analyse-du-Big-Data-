import scrapy
import json
from datetime import datetime

class CrossrefSpider(scrapy.Spider):
    name = 'crossref'
    allowed_domains = ['api.crossref.org']
    
    custom_settings = {
        'FEEDS': {
            'output/crossref.json': {
                'format': 'json',
                'overwrite': True,
                'indent': 2,
            },
        },
        'DOWNLOAD_DELAY': 1,
    }
    
    def __init__(self, max_articles=150, *args, **kwargs):
        super(CrossrefSpider, self).__init__(*args, **kwargs)
        self.max_articles = int(max_articles)
        self.article_count = 0
        self.base_url = 'https://api.crossref.org/works'
    
    def start_requests(self):
        params = {
            'rows': self.max_articles,
            'filter': 'type:journal-article,has-abstract:true,from-pub-date:2020',
            'select': 'DOI,title,author,abstract,container-title,ISSN,published-print,published-online,publisher,subject,URL'
        }
        url = f"{self.base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        yield scrapy.Request(url, callback=self.parse, headers={'User-Agent': 'ScientificScraper/1.0 (mailto:research@example.com)'})
    
    def parse(self, response):
        data = json.loads(response.text)
        items = data.get('message', {}).get('items', [])
        
        for item in items:
            if self.article_count >= self.max_articles:
                break
            
            authors = []
            affiliations = []
            for author in item.get('author', []):
                name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                if name:
                    authors.append(name)
                for aff in author.get('affiliation', []):
                    aff_name = aff.get('name', '')
                    if aff_name and aff_name not in affiliations:
                        affiliations.append(aff_name)
            
            published = item.get('published-print') or item.get('published-online') or {}
            date_parts = published.get('date-parts', [[None, None, None]])[0]
            year = date_parts[0] if len(date_parts) > 0 else None
            month = date_parts[1] if len(date_parts) > 1 else None
            
            abstract = item.get('abstract', '')
            if abstract and abstract.startswith('<jats:p>'):
                abstract = abstract.replace('<jats:p>', '').replace('</jats:p>', '').strip()
            
            article = {
                'article_id': item.get('DOI', '').replace('/', '_'),
                'source': 'crossref',
                'doi': item.get('DOI'),
                'title': item.get('title', [''])[0],
                'abstract': abstract,
                'authors': authors,
                'affiliations': affiliations,
                'journal': item.get('container-title', [''])[0],
                'issn': item.get('ISSN', [None])[0],
                'year': year,
                'month': month,
                'date_published': f"{year}-{month:02d}-01" if year and month else None,
                'keywords': item.get('subject', []),
                'url': item.get('URL'),
                'language': 'en',
                'scraped_at': datetime.now().isoformat(),
                'publisher': item.get('publisher'),
                'pdf_url': None,
                'citations': None,
                'views': None,
                'quartile': None,
                'h_index': None,
                'country': None,
                'university': None,
                'laboratory': None,
                'isbn': None,
                'categories': [],
                'subjects': item.get('subject', [])
            }
            
            self.article_count += 1
            yield article
