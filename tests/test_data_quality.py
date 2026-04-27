import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[2]").appName("dq-tests").getOrCreate()

def test_no_null_user_id(spark):
    data = [("evt-1", 1, "click"), ("evt-2", None, "view")]
    df = spark.createDataFrame(data, ["event_id", "user_id", "event_type"])
    null_count = df.filter(col("user_id").isNull()).count()
    assert null_count == 0, f"Found {null_count} null user_ids!"

def test_event_type_domain(spark):
    """Only allowed event types exist"""
    allowed = {"click", "view", "purchase"}
    data = [("evt-1", 1, "click"), ("evt-2", 2, "view"), ("evt-3", 3, "purchase")]
    df = spark.createDataFrame(data, ["event_id", "user_id", "event_type"])
    actual = {row["event_type"] for row in df.select("event_type").distinct().collect()}
    assert actual.issubset(allowed), f"Invalid types found: {actual - allowed}"

def test_user_id_range(spark):
    """user_id must be positive"""
    data = [("evt-1", 1, "click"), ("evt-2", -5, "view")]
    df = spark.createDataFrame(data, ["event_id", "user_id", "event_type"])
    invalid = df.filter(col("user_id") <= 0).count()
    assert invalid == 0, f"{invalid} rows have invalid user_id"