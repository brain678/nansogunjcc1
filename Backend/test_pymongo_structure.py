#!/usr/bin/env python
"""Explore pymongo package structure"""

import pymongo
import sys

print(f"PyMongo version: {pymongo.__version__}")
print(f"\nPyMongo package contents:")

try:
    import pymongo.asynchronous
    print("  - pymongo.asynchronous exists")
    print(f"    Contents: {dir(pymongo.asynchronous)}")
except ImportError as e:
    print(f"  - pymongo.asynchronous: NOT FOUND ({e})")

try:
    import pymongo.motor_asyncio
    print("  - pymongo.motor_asyncio exists")
except ImportError:
    print("  - pymongo.motor_asyncio: NOT FOUND")

try:
    import motor.motor_asyncio
    print("  - motor.motor_asyncio exists")
    from motor.motor_asyncio import AsyncIOMotorClient
    print(f"    AsyncIOMotorClient: {AsyncIOMotorClient}")
except ImportError as e:
    print(f"  - motor.motor_asyncio: NOT FOUND ({e})")

# Check for async in pymongo
print(f"\nChecking pymongo submodules:")
import os
pymongo_path = os.path.dirname(pymongo.__file__)
print(f"PyMongo location: {pymongo_path}")
subfolders = [d for d in os.listdir(pymongo_path) if os.path.isdir(os.path.join(pymongo_path, d))]
print(f"Subfolders: {subfolders}")
