"""
AURA-KG Neo4j Database Connection Test Script.
Validates database credentials and server responsiveness.
"""

import sys
import logging
from backend.database import Neo4jDatabase

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_connection():
    """Verify Neo4j connectivity and execute a simple query."""
    print("🔌 Testing Neo4j database connection...")
    db = Neo4jDatabase()
    
    if db.verify_connectivity():
        try:
            result = db.execute_read("RETURN 'AURA-KG Connected' AS message, datetime() AS timestamp")
            print("✅ Connection successful!")
            print(f"   Message: {result[0]['message']}")
            print(f"   Server Time: {result[0]['timestamp']}")
            return True
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            return False
        finally:
            db.close()
    else:
        print("❌ Could not connect to Neo4j database. Check credentials and Docker container status.")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)