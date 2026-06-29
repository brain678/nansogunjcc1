#!/usr/bin/env python
"""Find correct AsyncClient import"""

try:
    from pymongo.asynchronous.mongo_client import AsyncMongoClient
    print("✓ Found: pymongo.asynchronous.mongo_client.AsyncMongoClient")
except ImportError as e:
    print(f"✗ Not found: {e}")

try:
    from pymongo.asynchronous.client import AsyncClient
    print("✓ Found: pymongo.asynchronous.client.AsyncClient")
except ImportError as e:
    print(f"✗ Not found: {e}")

try:
    from pymongo.asynchronous.database import AsyncDatabase
    print("✓ Found: pymongo.asynchronous.database.AsyncDatabase")
except ImportError as e:
    print(f"✗ Not found: {e}")

# List what's in mongo_client module
import pymongo.asynchronous.mongo_client as mc
print(f"\nContents of pymongo.asynchronous.mongo_client:")
print([x for x in dir(mc) if not x.startswith('_')])
