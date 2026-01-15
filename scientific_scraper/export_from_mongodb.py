#!/usr/bin/env python3
"""
Export all articles from MongoDB to all_articles.json
"""

import json
from pymongo import MongoClient

print("="*60)
print("Exporting Articles from MongoDB")
print("="*60)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['scientific_articles']
collection = db['articles']

# Count total articles
total = collection.count_documents({})
print(f"\nTotal articles in MongoDB: {total}")

# Export all articles
print("\nExporting articles...")
articles = list(collection.find({}, {'_id': 0}))

print(f"Exported: {len(articles)} articles")

# Remove duplicates
seen = set()
unique_articles = []
for article in articles:
    article_id = article.get('article_id') or article.get('doi') or article.get('title')
    if article_id and article_id not in seen:
        seen.add(article_id)
        unique_articles.append(article)

print(f"Unique articles: {len(unique_articles)}")
print(f"Duplicates removed: {len(articles) - len(unique_articles)}")

# Write to file
import os
os.makedirs('hdfs_data', exist_ok=True)

output_file = 'hdfs_data/all_articles.json'
if os.path.exists(output_file):
    os.remove(output_file)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(unique_articles, f, indent=2, ensure_ascii=False)

print(f"\n✓ Created: {output_file}")
print(f"  Size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")

# Show breakdown by source
from collections import Counter
sources_count = Counter([a.get('source', 'unknown') for a in unique_articles])
print(f"\nBreakdown by source:")
for source, count in sources_count.items():
    print(f"  {source:10s}: {count:5d} articles")

print(f"\n{'='*60}")
print("✓ Ready for HDFS upload!")
print(f"{'='*60}")
