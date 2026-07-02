#!/usr/bin/env python3
"""
Find all orphaned documents - documents with database records but missing files.
Connects directly to MongoDB without requiring full app initialization.
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

async def find_orphaned_documents():
    """Find all documents whose files don't exist in the uploads directory."""
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from pymongo.errors import ConnectionFailure
    except ImportError as e:
        print(f"❌ Error: Required package not installed: {e}")
        print("Install with: pip install motor pymongo")
        return
    
    # Configuration
    mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DATABASE_NAME', 'nans_db')
    upload_dir = Path(__file__).parent / 'uploads'
    
    print("=" * 70)
    print("ORPHANED DOCUMENTS FINDER")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  MongoDB URL: {mongo_url}")
    print(f"  Database: {db_name}")
    print(f"  Upload Directory: {upload_dir}")
    
    # Check if upload directory exists
    if not upload_dir.exists():
        print(f"⚠️  Upload directory does not exist: {upload_dir}")
        return
    
    # Get list of files that exist
    existing_files = set(f.name for f in upload_dir.iterdir() if f.is_file())
    print(f"  Files in uploads: {len(existing_files)}")
    
    # Connect to MongoDB
    print(f"\n🔌 Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        # Verify connection
        await client.admin.command('ping')
        print("✓ Connected to MongoDB")
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure MongoDB is running")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    try:
        db = client[db_name]
        documents_collection = db['document']
        
        # Fetch all documents
        print(f"\n📋 Fetching all documents from database...")
        all_docs = await documents_collection.find({}).to_list(None)
        print(f"   Total documents in database: {len(all_docs)}")
        
        # Analyze documents
        orphaned = []
        valid = []
        no_url = []
        
        for doc in all_docs:
            file_url = doc.get('file_url', '')
            doc_id = str(doc.get('_id', 'unknown'))
            title = doc.get('title', 'Unknown')
            uploaded_by = doc.get('uploaded_by', 'unknown')
            uploaded_at = doc.get('uploaded_at', None)
            
            if not file_url:
                no_url.append({
                    'id': doc_id,
                    'title': title,
                    'uploaded_by': uploaded_by,
                    'uploaded_at': uploaded_at
                })
            else:
                # Extract filename from URL
                filename = Path(file_url).name
                
                if filename in existing_files:
                    valid.append({
                        'id': doc_id,
                        'title': title,
                        'filename': filename,
                        'uploaded_by': uploaded_by,
                        'uploaded_at': uploaded_at
                    })
                else:
                    orphaned.append({
                        'id': doc_id,
                        'title': title,
                        'filename': filename,
                        'file_url': file_url,
                        'uploaded_by': uploaded_by,
                        'uploaded_at': uploaded_at
                    })
        
        # Report results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        print(f"\n✓ Valid documents (file exists): {len(valid)}")
        if valid and len(valid) <= 20:
            for doc in valid[:20]:
                print(f"  • {doc['title']} ({doc['filename']}) - by {doc['uploaded_by']}")
            if len(valid) > 20:
                print(f"  ... and {len(valid) - 20} more")
        
        print(f"\n⚠️  No URL (missing file_url field): {len(no_url)}")
        for doc in no_url:
            print(f"  • ID: {doc['id']}")
            print(f"    Title: {doc['title']}")
            print(f"    Uploaded by: {doc['uploaded_by']}")
            print(f"    Uploaded at: {doc['uploaded_at']}")
        
        print(f"\n❌ ORPHANED (file missing): {len(orphaned)}")
        if orphaned:
            for doc in orphaned:
                print(f"\n  • Title: {doc['title']}")
                print(f"    ID: {doc['id']}")
                print(f"    Filename: {doc['filename']}")
                print(f"    URL: {doc['file_url']}")
                print(f"    Uploaded by: {doc['uploaded_by']}")
                print(f"    Uploaded at: {doc['uploaded_at']}")
        else:
            print("  (None found - all documents have their files! 🎉)")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total documents: {len(all_docs)}")
        print(f"  ✓ Valid: {len(valid)}")
        print(f"  ⚠️  No URL: {len(no_url)}")
        print(f"  ❌ Orphaned: {len(orphaned)}")
        
        if orphaned:
            print(f"\n💡 To delete orphaned documents, run:")
            print(f"   python delete_orphaned_documents.py")
            
            # Save orphaned docs to a file for reference
            import json
            orphaned_file = Path(__file__).parent / 'orphaned_documents.json'
            with open(orphaned_file, 'w') as f:
                json.dump(orphaned, f, indent=2, default=str)
            print(f"\n📄 Orphaned documents saved to: {orphaned_file}")
        
    finally:
        client.close()
        print("\n✓ Database connection closed")

if __name__ == "__main__":
    asyncio.run(find_orphaned_documents())
