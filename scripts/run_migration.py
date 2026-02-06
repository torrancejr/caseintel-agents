#!/usr/bin/env python3
"""
Run database migrations for CaseIntel AI Agents.
Connects to PostgreSQL and executes migration SQL files.
"""
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from the agents directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def get_db_connection():
    """Get database connection from DATABASE_URL environment variable."""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   Please set it in your .env file")
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        return None


def run_migration(conn, migration_file):
    """Run a single migration file."""
    print(f"\n🔄 Running migration: {migration_file.name}")
    
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        cursor = conn.cursor()
        cursor.execute(migration_sql)
        conn.commit()
        cursor.close()
        
        print(f"✅ Migration completed: {migration_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
        return False


def verify_tables(conn):
    """Verify that all expected tables were created."""
    print("\n🔍 Verifying tables...")
    
    expected_tables = [
        'analysis_jobs',
        'analysis_results',
        'agent_timeline_events',
        'witness_mentions',
        'agent_execution_logs'
    ]
    
    try:
        cursor = conn.cursor()
        
        for table_name in expected_tables:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            """, (table_name,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Get column count
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                """, (table_name,))
                
                column_count = cursor.fetchone()[0]
                print(f"   ✅ {table_name} ({column_count} columns)")
            else:
                print(f"   ❌ {table_name} (not found)")
                return False
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


def verify_views(conn):
    """Verify that all expected views were created."""
    print("\n🔍 Verifying views...")
    
    expected_views = [
        'v_document_analysis',
        'v_hot_documents',
        'v_privilege_analysis'
    ]
    
    try:
        cursor = conn.cursor()
        
        for view_name in expected_views:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name = %s
            """, (view_name,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"   ✅ {view_name}")
            else:
                print(f"   ❌ {view_name} (not found)")
                return False
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ View verification failed: {str(e)}")
        return False


def check_backend_tables(conn):
    """Check if required backend tables exist."""
    print("\n🔍 Checking backend tables...")
    
    required_tables = [
        'cases',
        'documents',
        'classifications',
        'users',
        'firms'
    ]
    
    try:
        cursor = conn.cursor()
        missing_tables = []
        
        for table_name in required_tables:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            """, (table_name,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"   ✅ {table_name}")
            else:
                print(f"   ❌ {table_name} (not found)")
                missing_tables.append(table_name)
        
        cursor.close()
        
        if missing_tables:
            print(f"\n⚠️  Missing backend tables: {', '.join(missing_tables)}")
            print("   Please run backend migrations first!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backend table check failed: {str(e)}")
        return False


def main():
    """Main migration runner."""
    print("=" * 70)
    print("CaseIntel AI Agents - Database Migration")
    print("=" * 70)
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return 1
    
    print("✅ Connected to database")
    
    # Check backend tables
    if not check_backend_tables(conn):
        print("\n❌ Backend tables not found. Please run backend migrations first.")
        conn.close()
        return 1
    
    # Get migration files
    migrations_dir = Path(__file__).parent.parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("\n❌ No migration files found in migrations/")
        conn.close()
        return 1
    
    print(f"\n📁 Found {len(migration_files)} migration file(s)")
    
    # Run migrations
    success = True
    for migration_file in migration_files:
        if not run_migration(conn, migration_file):
            success = False
            break
    
    if not success:
        print("\n❌ Migration failed. Database rolled back.")
        conn.close()
        return 1
    
    # Verify tables
    if not verify_tables(conn):
        print("\n❌ Table verification failed")
        conn.close()
        return 1
    
    # Verify views
    if not verify_views(conn):
        print("\n❌ View verification failed")
        conn.close()
        return 1
    
    # Close connection
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Migration completed successfully!")
    print("=" * 70)
    
    print("\nNext steps:")
    print("  1. Run verification: python scripts/verify_setup.py")
    print("  2. Start API: uvicorn src.api.main:app --reload")
    print("  3. Test endpoint: curl http://localhost:8000/health")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
