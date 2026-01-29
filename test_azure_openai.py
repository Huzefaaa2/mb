#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI connection and configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("AZURE OPENAI CONNECTION TEST")
print("=" * 60)

# Check environment variables
print("\n1. Checking Environment Variables:")
print("-" * 60)

api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print(f"✓ AZURE_OPENAI_API_KEY: {'SET' if api_key else 'NOT SET'}")
if api_key:
    print(f"  → {api_key[:10]}...{api_key[-10:]}")

print(f"✓ AZURE_OPENAI_ENDPOINT: {'SET' if endpoint else 'NOT SET'}")
if endpoint:
    print(f"  → {endpoint}")

print(f"✓ AZURE_OPENAI_DEPLOYMENT_GPT35: {'SET' if deployment else 'NOT SET'}")
if deployment:
    print(f"  → {deployment}")

print(f"✓ AZURE_OPENAI_API_VERSION: {'SET' if api_version else 'NOT SET'}")
if api_version:
    print(f"  → {api_version}")

# Check if all required env vars are set
if not all([api_key, endpoint, deployment, api_version]):
    print("\n❌ ERROR: Missing required environment variables!")
    sys.exit(1)

print("\n✓ All environment variables are set!")

# Try importing openai
print("\n2. Checking OpenAI Package:")
print("-" * 60)

try:
    from openai import AzureOpenAI
    print("✓ OpenAI package with AzureOpenAI imported successfully")
except ImportError as e:
    print(f"❌ ERROR: Cannot import AzureOpenAI from openai: {e}")
    sys.exit(1)

# Test Azure OpenAI connection
print("\n3. Testing Azure OpenAI Connection:")
print("-" * 60)

try:
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    print("✓ Azure OpenAI client initialized successfully")
    
    # Try a simple API call
    print("\n4. Testing API Call (Sending test request to Azure OpenAI):")
    print("-" * 60)
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Magic Bus Compass 360 is ready!' and nothing else."}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    print("✓ API call successful!")
    print(f"\nResponse from Azure OpenAI:")
    print(f"  → {response.choices[0].message.content}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Azure OpenAI is properly configured.")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"\nError Type: {type(e).__name__}")
    print("\nDebugging Info:")
    print(f"  Endpoint: {endpoint}")
    print(f"  Deployment: {deployment}")
    print(f"  API Version: {api_version}")
    sys.exit(1)
