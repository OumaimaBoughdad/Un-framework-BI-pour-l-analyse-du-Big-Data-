#!/bin/bash

echo "=========================================="
echo "BIG DATA BI PROJECT - MASTER SCRIPT"
echo "Complete Pipeline: Scrape → HDFS → Spark → Dashboard"
echo "=========================================="

# Activate virtual environment
cd /root/bigdata-bi-project
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing requirements..."
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

# Configuration
ARTICLES_PER_SOURCE=20

cd scientific_scraper

# Step 1: Scraping
echo ""
echo "[1/6] Scraping $ARTICLES_PER_SOURCE articles from each source..."
echo "  This may take 15-30 minutes..."
echo ""

scrapy crawl arxiv -a max_results=$ARTICLES_PER_SOURCE -o output/arxiv.json &
PID1=$!
scrapy crawl pubmed -a max_results=$ARTICLES_PER_SOURCE -o output/pubmed.json &
PID2=$!
scrapy crawl crossref -a max_articles=$ARTICLES_PER_SOURCE -o output/crossref.json &
PID3=$!

wait $PID1 && echo "  ✓ arXiv complete"
wait $PID2 && echo "  ✓ PubMed complete"
wait $PID3 && echo "  ✓ CrossRef complete"

# Step 2: Combine data
echo ""
echo "[2/6] Combining all scraped data..."
python3 combine_data_streaming.py

# Step 3: Upload to HDFS
echo ""
echo "[3/6] Uploading to HDFS..."
docker cp hdfs_data/all_articles.json namenode:/tmp/
docker exec namenode hdfs dfs -mkdir -p /bigdata/scientific_articles
docker exec namenode hdfs dfs -put -f /tmp/all_articles.json /bigdata/scientific_articles/
echo "  ✓ Uploaded to HDFS"

# Step 4: Verify HDFS
echo ""
echo "[4/6] Verifying HDFS..."
docker exec namenode hdfs dfs -ls -h /bigdata/scientific_articles/ | grep all_articles.json

# Step 5: Run Spark Analysis
echo ""
echo "[5/6] Running Spark analysis..."
cd ../phase3_spark
source ../venv/bin/activate
python3 notebooks/spark_analysis.py

# Step 6: Launch Dashboard
echo ""
echo "[6/6] Launching dashboard..."
echo ""
echo "=========================================="
echo "✓ PIPELINE COMPLETE!"
echo "=========================================="
echo ""
echo "Dashboard starting at http://localhost:8501"
echo "Press Ctrl+C to stop"
echo ""

streamlit run dashboard/dashboard.py
