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
    
    client = groq.Client(
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Make the API call
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say OK."}]
    )
    
    if response.choices and response.choices[0].message.content:
        ok("LLM access verified")
    else:
        fail("Empty response from LLM")
        
except Exception as e:
    fail("LLM test failed", e)


print("ALL TESTS PASSED")
sys.exit(0)
