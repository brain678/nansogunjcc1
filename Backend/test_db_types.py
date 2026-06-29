#!/usr/bin/env python
"""Test Beanie with different database objects"""

import inspect
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.asynchronous.client import AsyncClient

print("=== Testing different database types ===\n")

# Show what types are expected
print("Motor AsyncIOMotorDatabase:", type(AsyncIOMotorDatabase))
print("PyMongo AsyncClient:", type(AsyncClient))

# Test the actual types we're dealing with
print("\nChecking init_beanie parameter type hints:")
sig = inspect.signature(init_beanie)
db_param = sig.parameters['database']
print(f"database parameter annotation: {db_param.annotation}")
