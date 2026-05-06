#!/usr/bin/env python3
import requests

BASE = "http://127.0.0.1:8000"
endpoints = ["/api/activity", "/api/dashboard", "/api/kb"]

for ep in endpoints:
    url = BASE + ep
    try:
        r = requests.get(url, timeout=10)
        print(f"GET {ep} -> {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error calling {ep}: {e}")

print('\nDone')
