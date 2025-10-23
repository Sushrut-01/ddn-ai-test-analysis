# MongoDB Atlas (Cloud) Setup Guide

## 🌐 MongoDB Atlas vs Local MongoDB

You have **two options** for MongoDB:

### **Option 1: Local MongoDB** (Development/Testing)
- ✅ Already running on `localhost:27017`
- ✅ Good for: Development, testing, learning
- ✅ Setup: 2 minutes with `setup_mongodb.py`
- ✅ Cost: Free (local)

### **Option 2: MongoDB Atlas** (Production)
- ✅ You have: Cloud account at https://cloud.mongodb.com
- ✅ Good for: Production, team collaboration, backups
- ✅ Setup: 5 minutes (create cluster + connection string)
- ✅ Cost: Free tier available (512MB)

---

## 🚀 MongoDB Atlas Setup (5 Minutes)

### **Step 1: Access Your Atlas Account**

Your Atlas URL: https://cloud.mongodb.com/v2#/org/68dc1c4495ae3e552cffa964/projects

```
1. Open: https://cloud.mongodb.com
2. Login with your credentials
3. Select your organization
4. Go to Projects
```

---

### **Step 2: Create a Cluster (If Not Already Exists)**

```
1. Click "Build a Database" (or select existing cluster)
2. Choose plan:
   - FREE (M0) - Good for testing (512 MB storage)
   - SHARED (M2/M5) - Good for small production
   - DEDICATED - Production with high traffic

3. Cloud Provider: Choose AWS/GCP/Azure
4. Region: Choose closest to your location
5. Cluster Name: ddn-ai-cluster (or your choice)
6. Click "Create Cluster" (takes 3-5 minutes)
```

---

### **Step 3: Create Database User**

```
1. Go to: Security → Database Access
2. Click: "Add New Database User"
3. Authentication Method: Password
4. Username: ddn_admin (or your choice)
5. Password: Generate secure password (copy it!)
6. Database User Privileges: "Atlas admin" or "Read and write to any database"
7. Click: "Add User"
```

**Save these credentials:**
```
Username: ddn_admin
Password: [YOUR_PASSWORD_HERE]
```

---

### **Step 4: Configure Network Access**

```
1. Go to: Security → Network Access
2. Click: "Add IP Address"
3. Choose one:
   - "Add Current IP Address" (for your location)
   - "Allow Access from Anywhere" (0.0.0.0/0) - for testing only!
4. Click: "Confirm"
```

**Security Note:**
- For production, whitelist only your server IPs
- Never use "Allow Access from Anywhere" in production

---

### **Step 5: Get Connection String**

```
1. Go to: Deployment → Database
2. Click: "Connect" on your cluster
3. Choose: "Connect your application"
4. Driver: Python
5. Version: 3.12 or later
6. Copy the connection string:
```

**Connection String Format:**
```
mongodb+srv://ddn_admin:<password>@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Replace `<password>` with your actual password!**

---

### **Step 6: Create Database**

**Option A - MongoDB Compass (GUI):**
```
1. Open MongoDB Compass
2. Paste connection string (with password)
3. Click "Connect"
4. Click "Create Database"
5. Database Name: ddn_ai_project
6. Collection Name: builds
7. Click "Create Database"
```

**Option B - Python Script (Automated):**

Save as `setup_mongodb_atlas.py`:

```python
#!/usr/bin/env python3
"""
MongoDB Atlas Setup for DDN AI Project
Creates database and collections in Atlas cloud
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
import os

# ============================================================================
# CONFIGURATION - UPDATE THESE!
# ============================================================================

# Replace with your actual Atlas connection string
ATLAS_URI = "mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"

# Or use environment variable
# ATLAS_URI = os.getenv("MONGODB_ATLAS_URI")

DATABASE_NAME = "ddn_ai_project"

# ============================================================================

def setup_atlas():
    print("="*70)
    print("  DDN AI Project - MongoDB Atlas Setup")
    print("="*70)
    print()

    if "YOUR_PASSWORD" in ATLAS_URI or "xxxxx" in ATLAS_URI:
        print("❌ ERROR: Please update ATLAS_URI with your actual connection string!")
        print()
        print("Get it from:")
        print("1. MongoDB Atlas → Clusters → Connect")
        print("2. Choose 'Connect your application'")
        print("3. Copy connection string")
        print("4. Replace <password> with your actual password")
        print()
        return False

    print("🔌 Connecting to MongoDB Atlas...")
    print(f"   Database: {DATABASE_NAME}")
    print()

    try:
        # Connect to Atlas
        client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=10000)

        # Test connection
        client.admin.command('ping')
        print("✅ Connected to Atlas successfully!")
        print()

        # Get database
        db = client[DATABASE_NAME]

        # Get cluster info
        server_info = client.server_info()
        print(f"   MongoDB Version: {server_info.get('version', 'Unknown')}")
        print()

        # ================================================================
        # 1. BUILDS COLLECTION
        # ================================================================
        print("📦 Setting up 'builds' collection...")

        builds = db.builds

        # Create indexes
        builds.create_index([("build_id", ASCENDING)], unique=True)
        builds.create_index([("timestamp", DESCENDING)])
        builds.create_index([("status", ASCENDING)])
        builds.create_index([("job_name", ASCENDING)])
        builds.create_index([("aging_days", DESCENDING)])

        print("  ✅ Created indexes")

        # Sample data
        sample_build = {
            "build_id": "ATLAS_SAMPLE_12345",
            "job_name": "DDN-Smoke-Tests",
            "test_suite": "Health_Check_Suite",
            "status": "FAILURE",
            "build_url": "https://jenkins.example.com/job/12345",
            "timestamp": datetime.utcnow(),
            "repository": "your-org/ddn-repo",
            "branch": "main",
            "commit_sha": "abc123def456",
            "error_log": "NullPointerException at DDNStorage.java:127",
            "aging_days": 5,
            "has_analysis": False
        }

        if not builds.find_one({"build_id": "ATLAS_SAMPLE_12345"}):
            builds.insert_one(sample_build)
            print("  ✅ Inserted sample build")

        # ================================================================
        # 2. OTHER COLLECTIONS
        # ================================================================
        print("\n📝 Setting up other collections...")

        # Console logs
        db.console_logs.create_index([("build_id", ASCENDING)])

        # Test results
        db.test_results.create_index([("build_id", ASCENDING)])

        # Analysis solutions
        db.analysis_solutions.create_index([("build_id", ASCENDING)], unique=True)
        db.analysis_solutions.create_index([("analysis_timestamp", DESCENDING)])

        # Refinement history
        db.refinement_history.create_index([("build_id", ASCENDING)])

        print("  ✅ All collections configured")

        # ================================================================
        # SUMMARY
        # ================================================================
        print("\n" + "="*70)
        print("✅ MongoDB Atlas Setup Complete!")
        print("="*70)
        print()
        print(f"📊 Database: {DATABASE_NAME}")
        print(f"📍 Atlas Cluster: Connected")
        print()
        print("📦 Collections Created:")

        for coll_name in sorted(db.list_collection_names()):
            count = db[coll_name].count_documents({})
            print(f"  ✅ {coll_name:25} ({count} documents)")

        print()
        print("🎯 Next Steps:")
        print("  1. Update .env file with Atlas connection string")
        print("  2. Configure n8n with Atlas credentials")
        print("  3. Test connection with: python test_mongodb_atlas.py")
        print()
        print("📝 Connection String for .env:")
        print(f"  MONGODB_URI={ATLAS_URI.split('?')[0]}/{DATABASE_NAME}")
        print()

        client.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check connection string is correct")
        print("  2. Replace <password> with actual password")
        print("  3. Verify IP address is whitelisted")
        print("  4. Check database user has correct permissions")
        print()
        return False

if __name__ == "__main__":
    success = setup_atlas()
    exit(0 if success else 1)
```

**Run it:**
```bash
# Update the connection string in the file first!
python setup_mongodb_atlas.py
```

---

### **Step 7: Test Atlas Connection**

Save as `test_mongodb_atlas.py`:

```python
#!/usr/bin/env python3
"""Test MongoDB Atlas Connection"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

# Replace with your connection string
ATLAS_URI = "mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"
DATABASE = "ddn_ai_project"

def test_atlas():
    print("🔍 Testing MongoDB Atlas Connection...")
    print()

    if "YOUR_PASSWORD" in ATLAS_URI:
        print("❌ Please update ATLAS_URI in the script!")
        return False

    try:
        # Connect
        client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=10000)

        # Test connection
        client.admin.command('ping')
        print("✅ Atlas connection successful!")

        # Get database
        db = client[DATABASE]

        # List collections
        collections = db.list_collection_names()
        print(f"\n📦 Collections in '{DATABASE}':")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"  ✅ {coll}: {count} documents")

        # Test query
        sample = db.builds.find_one()
        if sample:
            print(f"\n📊 Sample build: {sample.get('build_id')}")

        print("\n✅ All tests passed!")

        client.close()
        return True

    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check connection string")
        print("  2. Verify password is correct")
        print("  3. Whitelist your IP address")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_atlas()
    exit(0 if success else 1)
```

---

## 🔐 Security Best Practices

### **1. Store Connection String Securely**

**In `.env` file:**
```bash
# MongoDB Atlas (Cloud)
MONGODB_ATLAS_URI=mongodb+srv://ddn_admin:YOUR_PASSWORD@cluster.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority

# Don't commit .env to Git!
```

**In n8n credentials:**
```
1. n8n → Settings → Credentials
2. Add MongoDB credential
3. Name: "MongoDB Atlas Production"
4. Connection String: [paste Atlas URI]
5. Save
```

### **2. Network Security**

```
Production Setup:
1. Atlas → Security → Network Access
2. Remove "Allow Access from Anywhere"
3. Add only your server IPs:
   - Production server IP
   - n8n server IP
   - Development IPs (temporary)
```

### **3. Database User Permissions**

```
For Production:
1. Create specific user for application
2. Grant only required permissions:
   - Read/Write to ddn_ai_project database
   - No admin access
3. Use strong password (20+ chars)
```

---

## 📊 Atlas vs Local Comparison

| Feature | Local MongoDB | MongoDB Atlas |
|---------|--------------|---------------|
| **Setup Time** | 2 minutes | 5 minutes |
| **Cost** | Free | Free tier (512MB) |
| **Backups** | Manual | Automatic |
| **Scalability** | Limited | Automatic |
| **Team Access** | Local only | Cloud access |
| **Monitoring** | Manual | Built-in dashboard |
| **Security** | Your responsibility | Managed |
| **Best For** | Development | Production |

---

## 🎯 Recommended Setup

### **Development:**
```
Use Local MongoDB
- Fast setup
- No internet required
- Good for testing
Connection: mongodb://localhost:27017/ddn_ai_project
```

### **Production:**
```
Use MongoDB Atlas
- Automatic backups
- Better security
- Team collaboration
- 99.9% uptime SLA
Connection: mongodb+srv://user:pass@cluster.mongodb.net/ddn_ai_project
```

---

## 🔄 Migration (Local → Atlas)

**When you're ready to move to Atlas:**

```bash
# 1. Export from local
mongodump --db=ddn_ai_project --out=backup/

# 2. Import to Atlas
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net" --db=ddn_ai_project backup/ddn_ai_project/

# 3. Update .env file
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ddn_ai_project

# 4. Update n8n credentials
# Replace local MongoDB credential with Atlas credential

# 5. Test workflows
# Run manual trigger test to verify connection
```

---

## 🔧 Configure n8n for Atlas

### **Update MongoDB Credentials:**

```
1. Open n8n: http://localhost:5678
2. Settings → Credentials
3. Find "MongoDB Production" credential
4. Update Connection String:
   mongodb+srv://ddn_admin:PASSWORD@cluster.xxxxx.mongodb.net/ddn_ai_project
5. Test Connection
6. Save
```

**All 3 workflows will automatically use Atlas!**

---

## 🧪 Test Atlas with Workflow

```bash
# Test manual trigger with Atlas
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{"build_id": "ATLAS_SAMPLE_12345", "user_email": "test@example.com"}'

# Verify in Atlas:
# 1. Go to Atlas → Clusters → Browse Collections
# 2. Database: ddn_ai_project
# 3. Collection: analysis_solutions
# 4. Should see new analysis document
```

---

## 📝 Connection String Format

### **Local MongoDB:**
```
mongodb://localhost:27017/ddn_ai_project
mongodb://username:password@localhost:27017/ddn_ai_project
```

### **MongoDB Atlas:**
```
mongodb+srv://username:password@cluster.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority
```

**Key Differences:**
- Atlas uses `mongodb+srv://` (not `mongodb://`)
- Atlas includes cluster hostname
- Atlas requires DNS SRV lookup
- Atlas typically includes `retryWrites=true&w=majority`

---

## ✅ Quick Decision Guide

### **Use Local MongoDB if:**
- ✅ Just learning/testing
- ✅ Working offline
- ✅ Single developer
- ✅ No backup needed

### **Use MongoDB Atlas if:**
- ✅ Production deployment
- ✅ Team collaboration
- ✅ Need automatic backups
- ✅ Want monitoring dashboard
- ✅ Require high availability

---

## 🎯 Recommendation

**For DDN AI Project:**

1. **Development/Testing**: Use local MongoDB
   - Setup: `python setup_mongodb.py`
   - Fast and simple

2. **Production**: Use MongoDB Atlas
   - Better for team access
   - Automatic backups
   - Professional monitoring

**Both work with the same workflows!** Just update the connection string.

---

## 📞 Support

**MongoDB Atlas Support:**
- Documentation: https://docs.atlas.mongodb.com/
- Community: https://community.mongodb.com/
- Your Atlas: https://cloud.mongodb.com

**Local MongoDB Setup:**
- See: [mongodb-setup-guide.md](mongodb-setup-guide.md)
- Quick Start: [MONGODB-QUICKSTART.md](../../MONGODB-QUICKSTART.md)

---

**Next Steps:**
1. Choose: Local (development) or Atlas (production)
2. Run setup script for your choice
3. Update n8n credentials
4. Test with workflows!

---

**Last Updated**: October 17, 2025
