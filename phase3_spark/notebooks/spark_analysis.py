#!/usr/bin/env python3
"""
Phase 3: Apache Spark Analysis
All 7 required analyses + TF-IDF + LDA + Weak Signals
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import HashingTF, IDF, Tokenizer, StopWordsRemover
from pyspark.ml.clustering import LDA

print("="*60)
print("PHASE 3: Apache Spark Analysis")
print("="*60)

# Initialize Spark
spark = SparkSession.builder \
    .appName("ScientificArticlesAnalysis") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

print(f"\nSpark version: {spark.version}")

# Load data
print("\n[1/11] Loading data...")
try:
    df = spark.read.option("multiline", "true").json("hdfs://localhost:9000/bigdata/scientific_articles/all_articles.json")
except:
    df = spark.read.option("multiline", "true").json("/root/bigdata-bi-project/scientific_scraper/hdfs_data/all_articles.json")

print(f"Total articles: {df.count()}")

# Analysis 1: Publications by Year
print("\n[2/11] Publications by year...")
publications_by_year = df.groupBy("year").agg(count("*").alias("count")).orderBy("year")
publications_by_year.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/publications_by_year.csv", header=True)
print(f"✓ Saved publications_by_year.csv")

# Analysis 2: Top Authors
print("\n[3/11] Top authors...")
authors_df = df.select(explode("authors").alias("author"), "article_id")
top_authors = authors_df.groupBy("author").agg(count("*").alias("publications")).orderBy(desc("publications")).limit(50)
top_authors.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/top_authors.csv", header=True)
print(f"✓ Saved top_authors.csv")

# Analysis 3: Co-author Network
print("\n[4/11] Co-author network...")
authors_exploded = df.select("article_id", explode("authors").alias("author"))
coauthors = authors_exploded.alias("a1").join(
    authors_exploded.alias("a2"),
    (col("a1.article_id") == col("a2.article_id")) & (col("a1.author") < col("a2.author"))
).select(col("a1.author").alias("author1"), col("a2.author").alias("author2"))
coauthor_network = coauthors.groupBy("author1", "author2").agg(count("*").alias("collaborations")).orderBy(desc("collaborations")).limit(100)
coauthor_network.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/coauthor_network.csv", header=True)
print(f"✓ Saved coauthor_network.csv")

# Analysis 4: Affiliations
print("\n[5/11] Top affiliations...")
affiliations_df = df.select(explode("affiliations").alias("affiliation"))
top_affiliations = affiliations_df.groupBy("affiliation").agg(count("*").alias("count")).orderBy(desc("count")).limit(30)
top_affiliations.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/top_affiliations.csv", header=True)
by_source = df.groupBy("source").count().orderBy(desc("count"))
by_source.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/by_source.csv", header=True)
print(f"✓ Saved top_affiliations.csv and by_source.csv")

# Analysis 5: Quartile Distribution
print("\n[6/11] Quartile distribution...")
# Assign mock quartiles based on journal prestige for demonstration
from pyspark.sql.functions import when

df_with_quartile = df.withColumn("quartile_assigned",
    when(lower(col("journal")).contains("nature") | 
         lower(col("journal")).contains("science") | 
         lower(col("journal")).contains("cell") |
         lower(col("journal")).contains("lancet"), "Q1")
    .when(lower(col("journal")).contains("ieee") | 
          lower(col("journal")).contains("acm") |
          lower(col("journal")).contains("plos"), "Q2")
    .when(col("journal").isNotNull(), "Q3")
    .otherwise("Q4")
)

quartile_dist = df_with_quartile.groupBy("quartile_assigned").agg(count("*").alias("count")).orderBy("quartile_assigned")
quartile_dist.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/quartile_distribution.csv", header=True)
print(f"✓ Saved quartile_distribution.csv (mock quartiles assigned)")

# Analysis 6: Keywords by Year
print("\n[7/11] Keywords by year...")
keywords_by_year = df.select("year", explode("keywords").alias("keyword")) \
    .filter(col("keyword").isNotNull()) \
    .groupBy("year", "keyword").agg(count("*").alias("frequency")).orderBy(desc("frequency"))
keywords_by_year.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/keywords_by_year.csv", header=True)
print(f"✓ Saved keywords_by_year.csv")

# Analysis 7: TF-IDF
print("\n[8/11] Computing TF-IDF...")
text_df = df.select("article_id", "abstract").filter(col("abstract").isNotNull())
tokenizer = Tokenizer(inputCol="abstract", outputCol="words")
words_df = tokenizer.transform(text_df)
remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
filtered_df = remover.transform(words_df)
hashingTF = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=1000)
tf_df = hashingTF.transform(filtered_df)
idf = IDF(inputCol="raw_features", outputCol="features")
idf_model = idf.fit(tf_df)
tfidf_df = idf_model.transform(tf_df)
print(f"✓ TF-IDF computed")

# Analysis 8: LDA
print("\n[9/11] Running LDA topic modeling...")
lda = LDA(k=10, maxIter=20, featuresCol="features")
lda_model = lda.fit(tfidf_df)
topics = lda_model.describeTopics(10)
print(f"✓ LDA completed with 10 topics")

# Analysis 9: Weak Signals
print("\n[10/11] Detecting weak signals...")
emerging_terms = ["federated learning", "quantum ml", "quantum machine learning", 
                  "explainable ai", "edge computing", "neuromorphic", "gpt", "llm"]
recent_df = df.filter(col("year") >= 2023)
weak_signals = []
for term in emerging_terms:
    term_count = recent_df.filter(
        lower(col("title")).contains(term.lower()) | 
        lower(col("abstract")).contains(term.lower())
    ).count()
    weak_signals.append((term, term_count))
weak_signals_df = spark.createDataFrame(weak_signals, ["term", "occurrences"]).orderBy(desc("occurrences"))
weak_signals_df.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/weak_signals.csv", header=True)
print(f"✓ Saved weak_signals.csv")

# Summary Stats
print("\n[11/11] Generating summary statistics...")
from pyspark.sql.functions import count as spark_count
summary_stats = df.agg(
    spark_count("article_id").alias("total_articles"),
    countDistinct("doi").alias("unique_dois"),
    min("year").alias("earliest_year"),
    max("year").alias("latest_year"),
    countDistinct("journal").alias("unique_journals")
)
summary_stats.write.mode("overwrite").csv("/root/bigdata-bi-project/phase3_spark/output/summary_stats.csv", header=True)
print(f"✓ Saved summary_stats.csv")

print("\n" + "="*60)
print("✓ Phase 3 Analysis Complete!")
print("="*60)
print("\nOutput files in: /root/bigdata-bi-project/phase3_spark/output/")
print("\nNext steps:")
print("1. Start API: python3 api/app.py")
print("2. Start Dashboard: streamlit run dashboard/dashboard.py")

spark.stop()
