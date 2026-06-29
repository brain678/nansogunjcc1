#!/usr/bin/env python
"""Test Beanie init_beanie signature"""

import inspect
from beanie import init_beanie

# Get the signature
sig = inspect.signature(init_beanie)
print(f"init_beanie signature: {sig}")
print(f"\nParameters:")
for param_name, param in sig.parameters.items():
    print(f"  {param_name}: {param.annotation} = {param.default}")
