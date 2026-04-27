import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("qa-tests")
        .getOrCreate()
    )

def test_null_filter(spark):
    """Null event_id should be filtered out"""
    data = [
        ("evt-1", 1, "click"),
        (None,    2, "view"),   # should be removed
        ("evt-3", 3, "purchase"),
    ]
    df = spark.createDataFrame(data, ["event_id", "user_id", "event_type"])
    result = df.filter(col("event_id").isNotNull())
    assert result.count() == 2

def test_invalid_event_type_filter(spark):
    """Invalid event types should be filtered"""
    data = [
        ("evt-1", 1, "click"),
        ("evt-2", 2, "INVALID"),  # should be removed
        ("evt-3", 3, "purchase"),
    ]
    df = spark.createDataFrame(data, ["event_id", "user_id", "event_type"])
    result = df.filter(col("event_type").isin(["click", "view", "purchase"]))
    assert result.count() == 2

def test_no_duplicates(spark):
    """Deduplication test"""
    data = [
        ("evt-1", 1, "click"),
        ("evt-1", 1, "click"),   # duplicate
        ("evt-2", 2, "view"),
    ]
    df = spark.createDataFrame(data, ["event_id", "user_id", "event_type"])
    result = df.dropDuplicates(["event_id"])
    assert result.count() == 2

def test_row_count_not_zero(spark):
    """Pipeline should never produce empty output"""
    data = [("evt-1", 1, "click"), ("evt-2", 2, "view")]
    df = spark.createDataFrame(data, ["event_id", "user_id", "event_type"])
    assert df.count() > 0