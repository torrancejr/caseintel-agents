#!/usr/bin/env python3
"""
Verification script to check that all required files and dependencies are present.
Run this after cloning the repository to verify the setup.
"""
import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def check_file(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"{GREEN}✓{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {filepath} (MISSING)")
        return False


def check_directory(dirpath, description):
    """Check if a directory exists."""
    if os.path.isdir(dirpath):
        print(f"{GREEN}✓{RESET} {description}: {dirpath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {dirpath} (MISSING)")
        return False


def check_env_var(var_name):
    """Check if an environment variable is set."""
    if os.getenv(var_name):
        print(f"{GREEN}✓{RESET} Environment variable: {var_name}")
        return True
    else:
        print(f"{YELLOW}⚠{RESET} Environment variable: {var_name} (NOT SET)")
        return False


def main():
    print("=" * 70)
    print("CaseIntel AI Agents - Setup Verification")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # Check project structure
    print("📁 Checking Project Structure...")
    print("-" * 70)
    
    required_files = [
        ("src/agents/base.py", "Base Agent"),
        ("src/agents/classifier.py", "Document Classifier"),
        ("src/agents/metadata_extractor.py", "Metadata Extractor"),
        ("src/agents/privilege_checker.py", "Privilege Checker"),
        ("src/agents/hot_doc_detector.py", "Hot Doc Detector"),
        ("src/agents/content_analyzer.py", "Content Analyzer"),
        ("src/agents/cross_reference.py", "Cross-Reference Engine"),
        ("src/workflows/state.py", "Pipeline State"),
        ("src/workflows/discovery_pipeline.py", "Discovery Pipeline"),
        ("src/models/database.py", "Database Models"),
        ("src/models/schemas.py", "Pydantic Schemas"),
        ("src/services/db.py", "Database Service"),
        ("src/services/s3.py", "S3 Service"),
        ("src/services/notifications.py", "Notification Service"),
        ("src/rag/chunking.py", "Document Chunking"),
        ("src/rag/embeddings.py", "Vector Embeddings"),
        ("src/rag/retrieval.py", "RAG Retrieval"),
        ("src/api/main.py", "FastAPI Main"),
        ("src/api/dependencies.py", "API Dependencies"),
        ("src/api/routes/health.py", "Health Route"),
        ("src/api/routes/analyze.py", "Analyze Route"),
        ("src/api/routes/status.py", "Status Route"),
        ("requirements.txt", "Requirements"),
        ("Dockerfile", "Dockerfile"),
        ("docker-compose.yml", "Docker Compose"),
        (".env.example", "Environment Template"),
        ("README.md", "README"),
    ]
    
    for filepath, description in required_files:
        if not check_file(filepath, description):
            all_checks_passed = False
    
    print()
    
    # Check directories
    print("📂 Checking Directories...")
    print("-" * 70)
    
    required_dirs = [
        ("src/agents", "Agents Directory"),
        ("src/workflows", "Workflows Directory"),
        ("src/models", "Models Directory"),
        ("src/services", "Services Directory"),
        ("src/rag", "RAG Directory"),
        ("src/api", "API Directory"),
        ("src/api/routes", "API Routes Directory"),
        ("tests", "Tests Directory"),
        ("scripts", "Scripts Directory"),
    ]
    
    for dirpath, description in required_dirs:
        if not check_directory(dirpath, description):
            all_checks_passed = False
    
    print()
    
    # Check environment variables
    print("🔐 Checking Environment Variables...")
    print("-" * 70)
    
    required_env_vars = [
        "ANTHROPIC_API_KEY",
        "DATABASE_URL",
        "CASEINTEL_API_KEY",
    ]
    
    optional_env_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET",
    ]
    
    env_checks_passed = True
    for var in required_env_vars:
        if not check_env_var(var):
            env_checks_passed = False
    
    print()
    print("Optional environment variables:")
    for var in optional_env_vars:
        check_env_var(var)
    
    print()
    
    # Check Python version
    print("🐍 Checking Python Version...")
    print("-" * 70)
    
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"{GREEN}✓{RESET} Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"{RED}✗{RESET} Python version: {python_version.major}.{python_version.minor}.{python_version.micro} (3.11+ required)")
        all_checks_passed = False
    
    print()
    
    # Check if dependencies are installed
    print("📦 Checking Dependencies...")
    print("-" * 70)
    
    required_packages = [
        "fastapi",
        "anthropic",
        "langchain",
        "langgraph",
        "chromadb",
        "sqlalchemy",
        "pydantic",
        "boto3",
    ]
    
    deps_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"{GREEN}✓{RESET} Package installed: {package}")
        except ImportError:
            print(f"{RED}✗{RESET} Package not installed: {package}")
            deps_installed = False
    
    print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    if all_checks_passed and deps_installed and env_checks_passed:
        print(f"{GREEN}✓ All checks passed!{RESET}")
        print()
        print("Your CaseIntel AI Agents setup is complete and ready to use.")
        print()
        print("Next steps:")
        print("1. Ensure all environment variables are set in .env file")
        print("2. Run: docker-compose up -d")
        print("3. Access API at: http://localhost:8000")
        print("4. View docs at: http://localhost:8000/docs")
        return 0
    else:
        print(f"{RED}✗ Some checks failed!{RESET}")
        print()
        if not all_checks_passed:
            print("- Some required files or directories are missing")
        if not deps_installed:
            print("- Some Python packages are not installed")
            print("  Run: pip install -r requirements.txt")
        if not env_checks_passed:
            print("- Some required environment variables are not set")
            print("  Copy .env.example to .env and fill in your values")
        return 1


if __name__ == "__main__":
    sys.exit(main())
