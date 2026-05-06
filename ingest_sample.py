#!/usr/bin/env python3
"""Ingest sample document into the knowledge base"""
import requests
from pathlib import Path

# Upload the sample document
file_path = Path("data/sample_workplace_conduct.txt")
if file_path.exists():
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "text/plain")}
        try:
            response = requests.post("http://127.0.0.1:8000/api/ingestion/upload", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
else:
    print("File not found")
