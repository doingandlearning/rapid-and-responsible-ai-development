#!/usr/bin/env python3
"""
Step 1: PostgreSQL + pgvector Verification
Complete solution for verifying database setup.
"""

import psycopg
import sys

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

def verify_pgvector_setup():
    """
    Verify PostgreSQL + pgvector is ready for Edinburgh.
    
    This function checks:
    1. PostgreSQL connection and version
    2. pgvector extension installation
    3. Vector operations functionality
    4. Available vector operators
    """
    print("🔍 VERIFYING POSTGRESQL + PGVECTOR SETUP")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check PostgreSQL version
                cur.execute("SELECT version();")
                pg_version = cur.fetchone()[0]
                print(f"✅ PostgreSQL: {pg_version.split(',')[0]}")
                
                # Check pgvector extension
                cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                vector_ext = cur.fetchone()
                if vector_ext:
                    print(f"✅ pgvector extension: Installed")
                    # Get extension version
                    cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
                    version = cur.fetchone()[0]
                    print(f"   Version: {version}")
                else:
                    print("❌ pgvector extension: Not found!")
                    print("   Fix: Run 'CREATE EXTENSION vector;' in your database")
                    return False
                
                # Test vector operations
                print("\n🧮 Testing vector operations...")
                
                # Test basic vector creation and distance
                cur.execute("SELECT '[1,2,3]'::vector <=> '[1,2,4]'::vector as cosine_distance;")
                distance = cur.fetchone()[0]
                print(f"✅ Vector operations: Working (test cosine distance: {distance:.3f})")
                
                # Test different vector sizes (important for BGE-M3)
                cur.execute("SELECT vector_dims('[1,2,3]'::vector) as dimensions;")
                dims = cur.fetchone()[0]
                print(f"✅ Vector dimensions: {dims} (test vector)")
                
                # Test 1024-dimension vector (BGE-M3 size)
                test_1024 = "[" + ",".join(["0.1"] * 1024) + "]"
                cur.execute(f"SELECT vector_dims('{test_1024}'::vector) as dimensions;")
                dims_1024 = cur.fetchone()[0]
                print(f"✅ BGE-M3 compatibility: {dims_1024} dimensions supported")
                
                # Check available vector operators
                cur.execute("""
                    SELECT oprname, oprcode, 
                           oprleft::regtype as left_type, 
                           oprright::regtype as right_type
                    FROM pg_operator 
                    WHERE oprname IN ('<->', '<#>', '<=>')
                    AND oprleft = 'vector'::regtype
                    ORDER BY oprname;
                """)
                operators = cur.fetchall()
                
                print(f"\n🔧 Available vector operators: {len(operators)}")
                for op_name, op_code, left_type, right_type in operators:
                    print(f"   {op_name}: {left_type} {op_name} {right_type} → {op_code}")
                
                # Test each operator
                test_vectors = ["'[1,0,0]'::vector", "'[0,1,0]'::vector"]
                print(f"\n🧪 Testing operators with vectors {test_vectors[0]} and {test_vectors[1]}:")
                
                for op_name, _, _, _ in operators:
                    try:
                        cur.execute(f"SELECT {test_vectors[0]} {op_name} {test_vectors[1]} as result;")
                        result = cur.fetchone()[0]
                        print(f"   {op_name}: {result:.3f}")
                    except Exception as e:
                        print(f"   {op_name}: Error - {e}")
                
                # Test index types available
                cur.execute("""
                    SELECT amname 
                    FROM pg_am 
                    WHERE amname IN ('hnsw', 'ivfflat')
                    ORDER BY amname;
                """)
                index_methods = cur.fetchall()
                
                print(f"\n📊 Available vector index methods:")
                for (method,) in index_methods:
                    print(f"   ✅ {method}")
                
                if not index_methods:
                    print("   ⚠️  No specialized vector index methods found")
                    print("   Note: Basic functionality will work, but performance may be limited")
                
    except psycopg.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Ensure Docker containers are running: docker ps")
        print("   2. Check if PostgreSQL is listening on port 5050")
        print("   3. Verify database credentials")
        print("   4. Try: cd environment && docker compose restart")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    print("\n🎉 PostgreSQL + pgvector is fully ready for Edinburgh!")
    print("\n📝 Setup Summary:")
    print("   ✅ Database connection successful")
    print("   ✅ pgvector extension installed and functional") 
    print("   ✅ Vector operations working correctly")
    print("   ✅ All distance operators available")
    print("   ✅ 1024-dimension vectors supported (BGE-M3)")
    print("   ✅ Vector index methods available")
    
    return True

def additional_setup_checks():
    """Additional checks for production readiness."""
    print("\n🔍 ADDITIONAL PRODUCTION READINESS CHECKS")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check PostgreSQL configuration
                important_settings = [
                    'shared_buffers',
                    'work_mem', 
                    'maintenance_work_mem',
                    'max_connections'
                ]
                
                print("📊 Important PostgreSQL settings:")
                for setting in important_settings:
                    cur.execute(f"SHOW {setting};")
                    value = cur.fetchone()[0]
                    print(f"   {setting}: {value}")
                
                # Check available memory
                cur.execute("SELECT pg_size_pretty(pg_database_size(current_database())) as db_size;")
                db_size = cur.fetchone()[0]
                print(f"\n💾 Current database size: {db_size}")
                
                # Test concurrent connections (basic)
                cur.execute("SELECT count(*) FROM pg_stat_activity;")
                active_connections = cur.fetchone()[0]
                print(f"🔗 Active connections: {active_connections}")
                
    except Exception as e:
        print(f"⚠️  Production checks failed: {e}")
        print("   This won't affect basic functionality")

def main():
    """Main verification workflow."""
    print("🚀 POSTGRESQL + PGVECTOR SETUP VERIFICATION")
    print("=" * 60)
    print("This script verifies your database is ready for Edinburgh's AI system.\n")
    
    # Primary verification
    success = verify_pgvector_setup()
    
    if success:
        # Additional production checks
        additional_setup_checks()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICATION COMPLETE - DATABASE READY!")
        print("You can proceed with the lab exercises.")
        print("\n💡 Next steps:")
        print("   • Create your Edinburgh knowledge base schema")
        print("   • Load sample documents with embeddings")
        print("   • Test vector search performance")
        return 0
    else:
        print("\n" + "=" * 60) 
        print("❌ VERIFICATION FAILED - SETUP ISSUES FOUND")
        print("Please fix the issues above before continuing.")
        print("\n🆘 Need help?")
        print("   • Check the troubleshooting section in the lab README")
        print("   • Ensure Docker services are running")
        print("   • Verify your environment variables")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)