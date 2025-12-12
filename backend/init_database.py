"""
Simple database initialization script
Creates and seeds the ReliefNet demo database
"""

import sqlite3
from pathlib import Path

# Paths
DB_DIR = Path(__file__).parent / "database"
DB_PATH = DB_DIR / "reliefnet.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
SEED_PATH = DB_DIR / "seed_data.sql"

print("Initializing ReliefNet Database...")
print(f"Database location: {DB_PATH}")

# Create directory
DB_DIR.mkdir(exist_ok=True)

# Remove existing database if it exists
if DB_PATH.exists():
    DB_PATH.unlink()
    print("Removed existing database")

# Create connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Execute schema
print("\nCreating tables...")
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    schema_sql = f.read()
    conn.executescript(schema_sql)
print(" Tables created")

# Execute seed data
print("\nInserting seed data...")
with open(SEED_PATH, 'r', encoding='utf-8') as f:
    seed_sql = f.read()
    conn.executescript(seed_sql)
print(" Seed data inserted")

# Verify
cursor.execute("SELECT COUNT(*) FROM warehouse_stock")
warehouses = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM public_requests")
requests = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM road_blockages")
blockages = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM vehicle_status")
vehicles = cursor.fetchone()[0]

conn.close()

print("\n" + "="*60)
print(" Database initialized successfully!")
print("="*60)
print(f"Warehouses: {warehouses}")
print(f"Public Requests: {requests}")
print(f"Road Blockages: {blockages}")
print(f"Vehicles: {vehicles}")
print("="*60)
