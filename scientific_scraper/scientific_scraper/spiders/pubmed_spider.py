import scrapy
import xmltodict
from datetime import datetime
from scientific_scraper.items import ScientificArticleItem
import time

class PubmedSpider(scrapy.Spider):
    name = 'pubmed'
    allowed_domains = ['eutils.ncbi.nlm.nih.gov']
    
    # Sujets liés au projet (adaptés pour PubMed)
    search_queries = [
        'machine learning',
        'artificial intelligence',
        'deep learning',
        'data mining',
        'big data analytics'
    ]
    
    def __init__(self, keywords=None, max_results=100, *args, **kwargs):
        super(PubmedSpider, self).__init__(*args, **kwargs)
        
        if keywords:
            self.search_queries = [keywords]
        
        self.max_results = max_results
        self.base_search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
        self.base_fetch_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
      
        # Inscrivez-vous sur https://www.ncbi.nlm.nih.gov/account/
        self.api_key = None 
    
    def start_requests(self):
        """
        Première étape : rechercher les IDs des articles
        """
        for query in self.search_queries:
            params = f"?db=pubmed&term={query.replace(' ', '+')}&retmax={self.max_results}&retmode=xml"
            
            if self.api_key:
                params += f"&api_key={self.api_key}"
            
            url = self.base_search_url + params
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_search_results,
                meta={'query': query},
                dont_filter=True
            )
    
    def parse_search_results(self, response):
        """
        Parse les résultats de recherche pour obtenir les IDs
        """
        data = xmltodict.parse(response.text)
        
        id_list = data.get('eSearchResult', {}).get('IdList', {}).get('Id', [])
        
        if isinstance(id_list, str):
            id_list = [id_list]
        
        if not id_list:
            self.logger.warning(f"No results found for query: {response.meta['query']}")
            return
        
        # Récupérer les détails par batch de 20 (limite de l'API)
        batch_size = 20
        for i in range(0, len(id_list), batch_size):
            batch = id_list[i:i+batch_size]
            ids = ','.join(batch)
            
            params = f"?db=pubmed&id={ids}&retmode=xml"
            
            if self.api_key:
                params += f"&api_key={self.api_key}"
            
            url = self.base_fetch_url + params
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_article_details,
                meta={'query': response.meta['query']},
                dont_filter=True
            )
            
            # Respecter les limites de l'API (3 requêtes/seconde sans clé API)
            if not self.api_key:
                time.sleep(0.34)
    
    def parse_article_details(self, response):
        """
        Parse les détails complets des articles
        """
        data = xmltodict.parse(response.text)
        
        articles = data.get('PubmedArticleSet', {}).get('PubmedArticle', [])
        
        if isinstance(articles, dict):
            articles = [articles]
        
        for article_data in articles:
            item = ScientificArticleItem()
            
            medline = article_data.get('MedlineCitation', {})
            article = medline.get('Article', {})
            
            # ID et source
            pmid = medline.get('PMID', {})
            if isinstance(pmid, dict):
                pmid = pmid.get('#text', '')
            
            item['article_id'] = pmid
            item['source'] = 'pubmed'
            
            # DOI
            article_ids = article_data.get('PubmedData', {}).get('ArticleIdList', {}).get('ArticleId', [])
            if isinstance(article_ids, dict):
                article_ids = [article_ids]
            
            for aid in article_ids:
                if isinstance(aid, dict) and aid.get('@IdType') == 'doi':
                    item['doi'] = aid.get('#text', '')
                    break
            else:
                item['doi'] = None
            
            # Titre
            item['title'] = article.get('ArticleTitle', '')
            
            # Résumé
            abstract_data = article.get('Abstract', {})
            if abstract_data:
                abstract_text = abstract_data.get('AbstractText', '')
                if isinstance(abstract_text, list):
                    item['abstract'] = ' '.join([
                        a.get('#text', a) if isinstance(a, dict) else str(a) 
                        for a in abstract_text
                    ])
                elif isinstance(abstract_text, dict):
                    item['abstract'] = abstract_text.get('#text', '')
                else:
                    item['abstract'] = abstract_text
            else:
                item['abstract'] = ''
            
            # Auteurs
            author_list = article.get('AuthorList', {}).get('Author', [])
            if isinstance(author_list, dict):
                author_list = [author_list]
            
            authors = []
            affiliations = []
            
            for author in author_list:
                # Nom complet
                last_name = author.get('LastName', '')
                fore_name = author.get('ForeName', '')
                
                if last_name and fore_name:
                    authors.append(f"{fore_name} {last_name}")
                elif last_name:
                    authors.append(last_name)
                
                # Affiliation
                affiliation_info = author.get('AffiliationInfo', {})
                if affiliation_info:
                    if isinstance(affiliation_info, list):
                        for aff in affiliation_info:
                            aff_text = aff.get('Affiliation', '')
                            if aff_text and aff_text not in affiliations:
                                affiliations.append(aff_text)
                    else:
                        aff_text = affiliation_info.get('Affiliation', '')
                        if aff_text and aff_text not in affiliations:
                            affiliations.append(aff_text)
            
            item['authors'] = authors
            item['affiliations'] = affiliations
            
            # Journal
            journal = article.get('Journal', {})
            item['journal'] = journal.get('Title', '')
            item['issn'] = journal.get('ISSN', {})
            if isinstance(item['issn'], dict):
                item['issn'] = item['issn'].get('#text', '')
            
            # Date de publication
            pub_date = article.get('ArticleDate', {}) or journal.get('JournalIssue', {}).get('PubDate', {})
            
            if pub_date:
                year = pub_date.get('Year', '')
                month = pub_date.get('Month', '')
                day = pub_date.get('Day', '01')
                
                item['year'] = int(year) if year else None
                
                # Convertir le mois
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                    'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                    'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                item['month'] = month_map.get(month, None)
                
                if year and month:
                    month_num = month_map.get(month, '01')
                    item['date_published'] = f"{year}-{month_num:02d}-{day if day else '01'}"
            
            # Mots-clés
            mesh_headings = medline.get('MeshHeadingList', {}).get('MeshHeading', [])
            if isinstance(mesh_headings, dict):
                mesh_headings = [mesh_headings]
            
            keywords = [response.meta['query']]
            for mesh in mesh_headings:
                descriptor = mesh.get('DescriptorName', {})
                if isinstance(descriptor, dict):
                    keywords.append(descriptor.get('#text', ''))
                else:
                    keywords.append(descriptor)
            
            item['keywords'] = keywords[:10]  # Limiter à 10 mots-clés
            
            # URL
            item['url'] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            # Métadonnées
            item['language'] = article.get('Language', ['en'])[0] if isinstance(article.get('Language'), list) else 'en'
            item['scraped_at'] = datetime.now().isoformat()
            item['publisher'] = None
            
            # Champs optionnels
            item['pdf_url'] = None
            item['citations'] = None
            item['views'] = None
            item['quartile'] = None
            item['h_index'] = None
            item['country'] = None
            item['university'] = None
            item['laboratory'] = None
            item['isbn'] = None
            item['categories'] = []
            item['subjects'] = keywords[:5]
            
            yield item
