#!/usr/bin/env python3
"""
Test database connection with detailed diagnostics
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 60)
print("Database Connection Test")
print("=" * 60)
print(f"\n📋 DATABASE_URL from .env:")
print(f"   {DATABASE_URL}")
print()

# Parse the URL to show components
if DATABASE_URL:
    parts = DATABASE_URL.replace("postgresql://", "").split("@")
    if len(parts) == 2:
        creds, location = parts
        user_pass = creds.split(":")
        host_db = location.split("/")
        
        print("📊 Parsed Components:")
        print(f"   User: {user_pass[0]}")
        print(f"   Password: {'*' * len(user_pass[1]) if len(user_pass) > 1 else 'N/A'}")
        print(f"   Host: {host_db[0]}")
        print(f"   Database: {host_db[1] if len(host_db) > 1 else 'N/A'}")
        print()

# Test connection
print("🔌 Testing connection...")
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print("✅ Connection successful!")
        print(f"\n📦 PostgreSQL Version:")
        print(f"   {version[:80]}...")
        print()
        
        # Test if tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('analysis_jobs', 'analysis_results', 'documents', 'cases')
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        print("📋 Relevant Tables:")
        for table in tables:
            print(f"   ✓ {table}")
        
        if 'analysis_jobs' not in tables:
            print("\n⚠️  Agent tables not found. Run migrations:")
            print("   psql -h localhost -p 5433 -U caseintel -d caseintel -f migrations/001-create-agents-tables.sql")
        
except Exception as e:
    print(f"❌ Connection failed!")
    print(f"\n🔍 Error Details:")
    print(f"   Type: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print()
    print("💡 Troubleshooting:")
    print("   1. Check if PostgreSQL is running:")
    print("      psql -h localhost -p 5433 -U caseintel -d caseintel")
    print("   2. Verify DATABASE_URL in .env file")
    print("   3. Check if port 5433 is correct (not 5432)")

print()
print("=" * 60)
