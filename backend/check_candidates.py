#!/usr/bin/env python3
"""Check recent candidates"""
import requests

try:
    response = requests.get('http://localhost:8000/api/candidates/')
    if response.status_code == 200:
        candidates = response.json()
        print(f'📋 Total candidates: {len(candidates)}')
        
        print('\n🔍 Recent candidates:')
        for c in candidates[-5:]:  # Last 5 candidates
            print(f'👤 {c["name"]} - {c["email"]}')
            print(f'   📊 Status: {c["status"]}')
            print(f'   🤖 AI Score: {c.get("ai_overall_score", "N/A")}')
            print(f'   📅 Created: {c["created_at"]}')
            print()
    else:
        print(f'❌ Error: {response.status_code}')
except Exception as e:
    print(f'❌ Error: {e}')
