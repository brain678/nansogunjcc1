#!/usr/bin/env python3
"""
Delete orphaned documents from MongoDB.
Use find_orphaned_documents.py first to identify them.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import List, Dict

async def delete_orphaned_documents():
    """Delete documents whose files don't exist in the uploads directory."""
    
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
    print("DELETE ORPHANED DOCUMENTS")
    print("=" * 70)
    
    # Check if upload directory exists
    if not upload_dir.exists():
        print(f"❌ Upload directory does not exist: {upload_dir}")
        return
    
    # Get list of files that exist
    existing_files = set(f.name for f in upload_dir.iterdir() if f.is_file())
    print(f"Upload directory: {upload_dir}")
    print(f"Files in uploads: {len(existing_files)}\n")
    
    # Connect to MongoDB
    print(f"🔌 Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("✓ Connected to MongoDB\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    try:
        db = client[db_name]
        documents_collection = db['document']
        
        # Fetch all documents
        all_docs = await documents_collection.find({}).to_list(None)
        print(f"Total documents in database: {len(all_docs)}\n")
        
        # Find orphaned documents
        orphaned_ids = []
        orphaned_details = []
        
        for doc in all_docs:
            file_url = doc.get('file_url', '')
            if file_url:
                filename = Path(file_url).name
                if filename not in existing_files:
                    orphaned_ids.append(doc['_id'])
                    orphaned_details.append({
                        'id': str(doc['_id']),
                        'title': doc.get('title', 'Unknown'),
                        'filename': filename,
                        'uploaded_by': doc.get('uploaded_by', 'unknown')
                    })
        
        if not orphaned_ids:
            print("✓ No orphaned documents found!")
            print("  All documents have their files in the uploads directory.")
            return
        
        # Show what will be deleted
        print(f"Found {len(orphaned_ids)} orphaned document(s) to delete:\n")
        for doc in orphaned_details:
            print(f"  • {doc['title']} (uploaded by {doc['uploaded_by']})")
            print(f"    ID: {doc['id']}")
            print(f"    Missing file: {doc['filename']}\n")
        
        # Confirm deletion
        response = input("⚠️  Are you sure you want to delete these orphaned documents? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Deletion cancelled")
            return
        
        # Delete orphaned documents
        print(f"\n🗑️  Deleting {len(orphaned_ids)} orphaned document(s)...")
        
        result = await documents_collection.delete_many({
            '_id': {'$in': orphaned_ids}
        })
        
        print(f"✓ Successfully deleted {result.deleted_count} document(s)\n")
        
        # Also delete from member.document_ids arrays
        print("🔗 Cleaning up member.document_ids references...")
        members_collection = db['member']
        
        # Convert ObjectIds to strings for matching
        orphaned_id_strings = [str(oid) for oid in orphaned_ids]
        
        result = await members_collection.update_many(
            {'document_ids': {'$in': orphaned_id_strings}},
            {'$pull': {'document_ids': {'$in': orphaned_id_strings}}}
        )
        
        if result.modified_count > 0:
            print(f"✓ Updated {result.modified_count} member record(s)\n")
        
        print("=" * 70)
        print("✓ CLEANUP COMPLETE")
        print("=" * 70)
        print(f"Deleted documents: {len(orphaned_ids)}")
        print(f"Updated members: {result.modified_count}")
        
    finally:
        client.close()
        print("\n✓ Database connection closed")

if __name__ == "__main__":
    asyncio.run(delete_orphaned_documents())
