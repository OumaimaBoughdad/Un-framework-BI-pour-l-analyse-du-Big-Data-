#!/bin/bash

echo "=========================================="
echo "HDFS Upload via Docker (Namenode)"
echo "=========================================="

# Copy file to namenode container
echo ""
echo "[1/5] Copying data to namenode container..."
docker cp /root/bigdata-bi-project/scientific_scraper/hdfs_data/all_articles.json namenode:/tmp/

# Create HDFS directory
echo ""
echo "[2/5] Creating HDFS directory..."
docker exec namenode hdfs dfs -mkdir -p /bigdata/scientific_articles

# Upload to HDFS
echo ""
echo "[3/5] Uploading to HDFS..."
docker exec namenode hdfs dfs -put -f /tmp/all_articles.json /bigdata/scientific_articles/

# Verify upload
echo ""
echo "[4/5] Verifying HDFS upload..."
docker exec namenode hdfs dfs -ls /bigdata/scientific_articles/
docker exec namenode hdfs dfs -du -h /bigdata/scientific_articles/

# Check content
echo ""
echo "[5/5] Checking file content (first 3 lines)..."
docker exec namenode hdfs dfs -cat /bigdata/scientific_articles/all_articles.json | head -3

echo ""
echo "=========================================="
echo "✓ Data uploaded to HDFS successfully!"
echo "=========================================="
echo ""
echo "HDFS Web UI: http://localhost:9870"
echo "  Navigate to: Utilities > Browse the file system"
echo "  Path: /bigdata/scientific_articles/all_articles.json"
