from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import glob

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = "/root/bigdata-bi-project/phase3_spark/output"

def load_csv(filename):
    """Load CSV file and return as dict"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        # Handle Spark CSV output (part files)
        if os.path.isdir(filepath):
            csv_files = glob.glob(os.path.join(filepath, "*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])
                return df.to_dict(orient='records')
        else:
            df = pd.read_csv(filepath)
            return df.to_dict(orient='records')
    return []

@app.route('/')
def home():
    return jsonify({
        "message": "Scientific Articles Analysis API",
        "endpoints": [
            "/api/publications-by-year",
            "/api/top-authors",
            "/api/coauthor-network",
            "/api/top-affiliations",
            "/api/quartile-distribution",
            "/api/keywords-by-year",
            "/api/weak-signals",
            "/api/summary-stats",
            "/api/by-source"
        ]
    })

@app.route('/api/publications-by-year')
def publications_by_year():
    data = load_csv('publications_by_year.csv')
    return jsonify(data)

@app.route('/api/top-authors')
def top_authors():
    limit = request.args.get('limit', 20, type=int)
    data = load_csv('top_authors.csv')
    return jsonify(data[:limit])

@app.route('/api/coauthor-network')
def coauthor_network():
    limit = request.args.get('limit', 50, type=int)
    data = load_csv('coauthor_network.csv')
    return jsonify(data[:limit])

@app.route('/api/top-affiliations')
def top_affiliations():
    limit = request.args.get('limit', 20, type=int)
    data = load_csv('top_affiliations.csv')
    return jsonify(data[:limit])

@app.route('/api/quartile-distribution')
def quartile_distribution():
    data = load_csv('quartile_distribution.csv')
    return jsonify(data)

@app.route('/api/keywords-by-year')
def keywords_by_year():
    year = request.args.get('year', type=int)
    data = load_csv('keywords_by_year.csv')
    if year:
        data = [d for d in data if d.get('year') == year]
    return jsonify(data[:100])

@app.route('/api/weak-signals')
def weak_signals():
    data = load_csv('weak_signals.csv')
    return jsonify(data)

@app.route('/api/summary-stats')
def summary_stats():
    data = load_csv('summary_stats.csv')
    return jsonify(data[0] if data else {})

@app.route('/api/by-source')
def by_source():
    data = load_csv('by_source.csv')
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
