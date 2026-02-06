#!/usr/bin/env python3
"""
Verify CaseIntel setup and configuration.
Checks database, AWS Bedrock, ChromaDB, embeddings, and all dependencies.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def check_env_vars():
    """Check required environment variables."""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "DATABASE_URL",
        "CASEINTEL_API_KEY"
    ]
    
    model_vars = [
        "MODEL_CLASSIFIER",
        "MODEL_METADATA",
        "MODEL_PRIVILEGE",
        "MODEL_HOTDOC",
        "MODEL_CONTENT",
        "MODEL_CROSSREF",
        "EMBEDDING_MODEL"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        return False
    
    print("✅ All required environment variables set")
    
    # Check model configuration
    missing_models = []
    for var in model_vars:
        if not os.getenv(var):
            missing_models.append(var)
    
    if missing_models:
        print(f"⚠️  Missing model configuration: {', '.join(missing_models)}")
        print("   Using default models")
    else:
        print("✅ Model configuration complete")
        print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"   Embedding Model: {os.getenv('EMBEDDING_MODEL', 'not set')}")
    
    return True


def check_database():
    """Check database connection."""
    print("\n🔍 Checking database connection...")
    
    try:
        from models.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("   Make sure PostgreSQL is running:")
        print("   docker-compose up -d postgres")
        return False


def check_bedrock():
    """Check AWS Bedrock access and models."""
    print("\n🔍 Checking AWS Bedrock access...")
    
    try:
        import boto3
        
        region = os.getenv("AWS_REGION", "us-east-1")
        
        # Check runtime access
        runtime_client = boto3.client(
            "bedrock-runtime",
            region_name=region
        )
        
        # Check model access
        bedrock_client = boto3.client(
            "bedrock",
            region_name=region
        )
        
        response = bedrock_client.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        print(f"✅ AWS Bedrock access successful ({len(models)} models available)")
        
        # Check specific models
        model_ids = [
            os.getenv("MODEL_CLASSIFIER"),
            os.getenv("MODEL_PRIVILEGE"),
            os.getenv("EMBEDDING_MODEL")
        ]
        
        available_model_ids = [m['modelId'] for m in models]
        
        for model_id in model_ids:
            if model_id:
                if model_id in available_model_ids:
                    print(f"   ✅ {model_id}")
                else:
                    print(f"   ⚠️  {model_id} (not found in available models)")
        
        return True
    except Exception as e:
        print(f"❌ AWS Bedrock access failed: {str(e)}")
        print("   Check your AWS credentials and region")
        return False


def check_embeddings():
    """Check embedding model access."""
    print("\n🔍 Checking embedding model...")
    
    try:
        import boto3
        import json
        
        embedding_model = os.getenv("EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        client = boto3.client(
            "bedrock-runtime",
            region_name=region
        )
        
        # Test embedding generation
        if "titan" in embedding_model.lower():
            body = json.dumps({"inputText": "test"})
        elif "cohere" in embedding_model.lower():
            body = json.dumps({"texts": ["test"], "input_type": "search_document"})
        else:
            print(f"⚠️  Unknown embedding model type: {embedding_model}")
            return True
        
        response = client.invoke_model(
            modelId=embedding_model,
            body=body
        )
        
        response_body = json.loads(response["body"].read())
        
        if "titan" in embedding_model.lower():
            embedding = response_body.get("embedding", [])
        elif "cohere" in embedding_model.lower():
            embedding = response_body.get("embeddings", [[]])[0]
        
        print(f"✅ Embedding model working: {embedding_model}")
        print(f"   Embedding dimensions: {len(embedding)}")
        return True
        
    except Exception as e:
        print(f"❌ Embedding model check failed: {str(e)}")
        print(f"   Model: {os.getenv('EMBEDDING_MODEL', 'not set')}")
        return False


def check_chromadb():
    """Check ChromaDB setup."""
    print("\n🔍 Checking ChromaDB...")
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        
        # Try to create a test collection
        test_collection = client.get_or_create_collection("test_setup")
        client.delete_collection("test_setup")
        
        print(f"✅ ChromaDB working (persist_dir: {persist_dir})")
        return True
    except Exception as e:
        print(f"❌ ChromaDB check failed: {str(e)}")
        return False


def check_imports():
    """Check all required imports."""
    print("\n🔍 Checking Python dependencies...")
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2",
        "chromadb",
        "boto3",
        "langgraph",
        "pydantic"
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing Python modules: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required Python modules installed")
    return True


def check_agents():
    """Check agent imports and configuration."""
    print("\n🔍 Checking agent configuration...")
    
    try:
        from agents.classifier import DocumentClassifier
        from agents.metadata_extractor import MetadataExtractor
        from agents.privilege_checker import PrivilegeChecker
        from agents.hot_doc_detector import HotDocDetector
        from agents.content_analyzer import ContentAnalyzer
        from agents.cross_reference import CrossReferenceEngine
        
        print("✅ All agents imported successfully")
        
        # Show model assignments
        print("\n   Agent Model Assignments:")
        print(f"   • Classifier: {os.getenv('MODEL_CLASSIFIER', 'default')}")
        print(f"   • Metadata: {os.getenv('MODEL_METADATA', 'default')}")
        print(f"   • Privilege: {os.getenv('MODEL_PRIVILEGE', 'default')}")
        print(f"   • Hot Doc: {os.getenv('MODEL_HOTDOC', 'default')}")
        print(f"   • Content: {os.getenv('MODEL_CONTENT', 'default')}")
        print(f"   • Cross-Ref: {os.getenv('MODEL_CROSSREF', 'default')}")
        
        return True
    except Exception as e:
        print(f"❌ Agent import failed: {str(e)}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("CaseIntel Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Environment Variables", check_env_vars),
        ("Python Dependencies", check_imports),
        ("Agent Configuration", check_agents),
        ("Database Connection", check_database),
        ("AWS Bedrock Access", check_bedrock),
        ("Embedding Model", check_embeddings),
        ("ChromaDB", check_chromadb)
    ]
    
    results = []
    for name, check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"❌ {name} check failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n🚀 Your CaseIntel setup is ready!")
        print("\nNext steps:")
        print("  1. Start services: docker-compose up -d")
        print("  2. Run API: uvicorn api.main:app --reload")
        print("  3. Test endpoint: curl http://localhost:8000/health")
        return 0
    else:
        print(f"⚠️  Some checks failed ({passed}/{total} passed)")
        print("\n📝 Please fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
