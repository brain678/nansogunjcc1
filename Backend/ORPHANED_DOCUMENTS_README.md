# Orphaned Documents Management Scripts

These scripts help you identify and remove orphaned document records from MongoDB - documents that have database entries but missing files in the uploads directory.

## Overview

**Orphaned documents** occur when:
- A document record exists in MongoDB
- But the corresponding file doesn't exist in the `/uploads` directory
- This causes 404 errors when trying to display/download the document

## Prerequisites

Make sure you have the required Python package installed:

```bash
pip install motor pymongo
```

## Scripts

### 1. `find_orphaned_documents.py` - Find Orphaned Documents

**Purpose:** Scan the database and identify all orphaned documents

**Usage:**
```bash
python find_orphaned_documents.py
```

**Environment Variables:**
- `MONGODB_URL` - MongoDB connection string (default: `mongodb://localhost:27017`)
- `DATABASE_NAME` - Database name (default: `nans_db`)

**Output:**
- Lists all orphaned documents with details (title, ID, uploaded by, filename)
- Shows valid documents and documents with missing URLs
- Generates `orphaned_documents.json` with detailed information
- Summary statistics

**Example:**
```bash
# With custom MongoDB URL
MONGODB_URL=mongodb://user:pass@localhost:27017 python find_orphaned_documents.py
```

### 2. `delete_orphaned_documents.py` - Delete Orphaned Documents

**Purpose:** Remove orphaned document records from the database

**Usage:**
```bash
python delete_orphaned_documents.py
```

**What it does:**
1. Finds all orphaned documents (same logic as find_orphaned_documents.py)
2. Shows you what will be deleted
3. Asks for confirmation (type 'yes' to proceed)
4. Deletes the orphaned document records
5. Removes orphaned document IDs from member.document_ids arrays

**Important:** This script **does not delete files** - it only removes database records

## Workflow

### Step 1: Identify Orphaned Documents
```bash
python find_orphaned_documents.py
```

Review the output to see:
- Which documents are orphaned
- How many there are
- Who uploaded them

### Step 2: Delete (Optional)
If you want to remove orphaned documents from the database:

```bash
python delete_orphaned_documents.py
```

You'll be prompted to confirm before deletion.

### Step 3: Verify
Run find_orphaned_documents.py again to confirm:
```bash
python find_orphaned_documents.py
```

Should show: `❌ ORPHANED (file missing): 0`

## Common Issues

### "Connection failed: Error connecting to 'mongodb://localhost:27017'"
MongoDB is not running. Start your MongoDB instance:
```bash
# Windows with MongoDB installed
mongod

# Or with Docker
docker run -d -p 27017:27017 mongo:latest
```

### "ModuleNotFoundError: No module named 'motor'"
Install the required package:
```bash
pip install motor pymongo
```

### Connection Timeout on Remote MongoDB
Make sure your MongoDB URL is correct and the server is accessible:
```bash
MONGODB_URL=mongodb://host:port/database python find_orphaned_documents.py
```

## API Integration

These scripts connect directly to MongoDB and work independently of the FastAPI application.

### For Local Development:
```bash
# Ensure MongoDB is running on localhost:27017
python find_orphaned_documents.py
```

### For Production:
```bash
# Set connection string to your production MongoDB
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net DATABASE_NAME=nans_db python find_orphaned_documents.py
```

## Cleanup Results

After running `delete_orphaned_documents.py`:

1. **MongoDB Documents**: Orphaned document records are removed
2. **Member References**: Document IDs are removed from `member.document_ids` arrays
3. **Files**: NOT deleted (they don't exist anyway)
4. **API**: GET endpoints will return 404 for references to deleted IDs (expected behavior)

## Safety Notes

- ✓ Scripts only modify MongoDB documents
- ✓ No files are deleted
- ✓ Deletion prompts for confirmation
- ✓ Uses MongoDB transactions where appropriate
- ✓ Backup your database before running delete script if concerned

## Example Output

### Find Orphaned Documents:
```
======================================================================
ORPHANED DOCUMENTS FINDER
======================================================================

Configuration:
  MongoDB URL: mongodb://localhost:27017
  Database: nans_db
  Upload Directory: C:\path\to\Backend\uploads
  Files in uploads: 45

🔌 Connecting to MongoDB...
✓ Connected to MongoDB

📋 Fetching all documents from database...
   Total documents in database: 50

======================================================================
RESULTS
======================================================================

✓ Valid documents (file exists): 47

❌ ORPHANED (file missing): 2

  • Profile Photo (by member@example.com)
    ID: 507f1f77bcf86cd799439011
    Filename: 97bac588981640448ecc67ed27e83b22.jpeg
    URL: /uploads/97bac588981640448ecc67ed27e83b22.jpeg
```

## Support

For issues or questions, check:
1. MongoDB connection string is correct
2. Motor and PyMongo are installed
3. Database name is correct
4. You have read/write permissions to the database
