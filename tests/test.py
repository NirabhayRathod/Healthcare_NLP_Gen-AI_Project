import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def fail(message, error=None):
    print(f"TEST FAILED: {message}")
    if error:
        print(error)
    sys.exit(1)

def ok(message):
    print(f"OK: {message}")

load_dotenv()

required_envs = [
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
    "GROQ_API_KEY",
]

for var in required_envs:
    if not os.getenv(var):
        fail(f"Missing environment variable: {var}")
    ok(f"{var} loaded")

try:
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{int(os.getenv('DB_PORT'))}/{os.getenv('DB_NAME')}",
        pool_pre_ping=True
    )

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    ok("Database connection successful")
except Exception as e:
    fail("Database connection failed", e)


try:
    tables_df = pd.read_sql("SHOW TABLES", engine)
    tables = tables_df.iloc[:, 0].tolist()

    for table in ["raw_data", "processed_data"]:
        if table not in tables:
            fail(f"Table not found: {table}")
        ok(f"Table exists: {table}")
except Exception as e:
    fail("Table existence check failed", e)


try:
    count_df = pd.read_sql(
        "SELECT COUNT(*) AS count FROM processed_data",
        engine
    )
    row_count = int(count_df["count"][0])

    if row_count <= 0:
        fail("processed_data table is empty")

    ok(f"processed_data contains {row_count} rows")
except Exception as e:
    fail("Data availability check failed", e)

try:
    sample_df = pd.read_sql(
        "SELECT drugName, review FROM processed_data LIMIT 1",
        engine
    )

    if sample_df.empty:
        fail("No sample data returned")

    ok("Sample data fetched successfully")
except Exception as e:
    fail("Sample data fetch failed", e)


try:
    import groq
    from langchain_groq import ChatGroq

    # Monkey-patch groq.Client to ignore 'proxies' argument
    original_init = groq.Client.__init__
    
    def patched_init(self, *args, **kwargs):
        # Remove 'proxies' if present (your groq version doesn't accept it)
        kwargs.pop('proxies', None)
        original_init(self, *args, **kwargs)
    
    groq.Client.__init__ = patched_init

    # Now initialize ChatGroq normally
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    response = llm.invoke("Say OK.")

    if not response.content:
        fail("Empty response from LLM")

    ok("LLM access verified")
except Exception as e:
    fail("LLM test failed", e)


print("ALL TESTS PASSED")
sys.exit(0)
