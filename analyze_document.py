#!/usr/bin/env python3
"""
Simple script to analyze a document via the API
"""
import sys
import json
import requests

def analyze_document(file_path, case_id, document_id, api_key):
    """Analyze a document"""
    with open(file_path, 'r') as f:
        document_text = f.read()
    
    payload = {
        "document_text": document_text,
        "case_id": case_id,
        "document_id": document_id
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    )
    
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: analyze_document.py <file_path> <case_id> <document_id> <api_key>")
        sys.exit(1)
    
    result = analyze_document(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(json.dumps(result, indent=2))
