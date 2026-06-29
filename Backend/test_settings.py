#!/usr/bin/env python
"""Test script to verify settings loading"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Print environment info
print(f"Current working directory: {Path.cwd()}")
print(f"Script location: {Path(__file__).parent}")

# Get PROJECT_ROOT the same way as in config
PROJECT_ROOT = Path(__file__).parent

print(f"\nPROJECT_ROOT: {PROJECT_ROOT}")
print(f"PROJECT_ROOT abs: {PROJECT_ROOT.absolute()}")

env_file_path = PROJECT_ROOT / ".env"
print(f"Env file path: {env_file_path}")
print(f"Env file exists: {env_file_path.exists()}")

# Load .env manually first
print("\n=== Loading .env with load_dotenv ===")
load_dotenv(env_file_path)

# Check environment variables
print(f"MONGODB_URL from env: {os.getenv('MONGODB_URL')}")
print(f"DATABASE_NAME from env: {os.getenv('DATABASE_NAME')}")

# Now import settings
print("\n=== Importing settings ===")
from app.core.config import settings

print(f"MONGODB_URL from settings: {settings.MONGODB_URL}")
print(f"DATABASE_NAME from settings: {settings.DATABASE_NAME}")
