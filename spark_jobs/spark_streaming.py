from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, current_date
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

S3_BUCKET = "s3a://your-bucket-name"   # replace with your bucket

spark = (
    SparkSession.builder
    .appName("kafka-to-s3")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
    .getOrCreate()
)

schema = StructType([
    StructField("event_id",   StringType(),  False),
    StructField("user_id",    IntegerType(), False),
    StructField("event_type", StringType(),  False),
    StructField("ts",         StringType(),  False),
])

raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "events")
    .option("startingOffsets", "earliest")
    .load()
)

parsed = (
    raw.select(from_json(col("value").cast("string"), schema).alias("j"))
       .select("j.*")
       .withColumn("event_ts", to_timestamp(col("ts")))
       .filter(col("event_id").isNotNull())
       .filter(col("event_type").isin(["click", "view", "purchase"]))
       .withColumn("dt", current_date())
       .drop("ts")
)

query = (
    parsed.writeStream
    .format("parquet")
    .option("path", f"{S3_BUCKET}/raw/")
    .option("checkpointLocation", f"{S3_BUCKET}/checkpoints/raw/")
    .outputMode("append")
    .trigger(processingTime="30 seconds")
    .start()
)

query.awaitTermination()