# MongoDB Atlas Cloud Setup for DDN AI System

**Using your MongoDB Atlas account instead of local MongoDB**

---

## Why Use MongoDB Atlas?

✅ **Cloud-based** - Access from anywhere
✅ **Automatic backups** - Data safety
✅ **Scalable** - Grows with your needs
✅ **Free tier** - 512MB storage free
✅ **Production-ready** - Enterprise features
✅ **No local installation** - Docker not needed for DB

---

## Step 1: Access Your MongoDB Atlas Account

You already have an account at:
```
https://cloud.mongodb.com/v2/68dc1c4495ae3e552cffaa08#/overview
```

**Login credentials:**
- Use your existing MongoDB Atlas login

---

## Step 2: Create a Cluster (if not exists)

### Check Existing Cluster

1. **Go to:** https://cloud.mongodb.com/v2/68dc1c4495ae3e552cffaa08#/clusters
2. **Look for:** Existing clusters

### If No Cluster Exists, Create One

1. Click **"Build a Database"** or **"Create"**
2. Choose **"M0 FREE"** tier
3. **Cloud Provider:** AWS, Google Cloud, or Azure (your choice)
4. **Region:** Choose closest to you (e.g., us-east-1, eu-west-1)
5. **Cluster Name:** `ddn-ai-cluster`
6. Click **"Create Cluster"**

**Wait:** 3-5 minutes for cluster to be created

---

## Step 3: Configure Database Access

### Create Database User

1. Go to **"Database Access"** (left sidebar)
2. Click **"Add New Database User"**
3. **Authentication Method:** Password
4. **Username:** `ddn_admin`
5. **Password:** Generate a secure password (save it!)
   - Example: `MySecure123!Pass`
   - **SAVE THIS PASSWORD** - you'll need it
6. **Database User Privileges:**
   - Choose **"Read and write to any database"**
7. Click **"Add User"**

---

## Step 4: Configure Network Access

### Allow Your IP Address

1. Go to **"Network Access"** (left sidebar)
2. Click **"Add IP Address"**
3. Choose one:

**Option A: Allow from anywhere** (easier for testing)
```
IP Address: 0.0.0.0/0
Description: Allow from anywhere
```

**Option B: Allow specific IPs** (more secure)
```
IP Address: Your current IP (auto-detected)
Description: My development machine
```

4. Click **"Confirm"**

**Note:** For Docker services, use "Allow from anywhere" (0.0.0.0/0)

---

## Step 5: Get Connection String

### From Atlas Dashboard

1. Go to **"Database"** → **"Clusters"**
2. Click **"Connect"** button on your cluster
3. Choose **"Connect your application"**
4. **Driver:** Python, Version: 3.12 or later
5. **Copy the connection string:**

```
mongodb+srv://ddn_admin:<password>@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### Modify Connection String

Replace `<password>` with your actual password:

**Before:**
```
mongodb+srv://ddn_admin:<password>@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**After:**
```
mongodb+srv://ddn_admin:MySecure123!Pass@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**IMPORTANT:**
- URL-encode special characters in password
- If password has `@`, `#`, `!` etc., use encoding:
  - `@` → `%40`
  - `#` → `%23`
  - `!` → `%21`

**Example with special chars:**
```
Password: MyPass@123!
Encoded: MyPass%40123%21
Connection: mongodb+srv://ddn_admin:MyPass%40123%21@ddn-ai-cluster...
```

---

## Step 6: Create Database and Collections

### Option A: Using MongoDB Compass (GUI)

1. **Download MongoDB Compass:**
   - https://www.mongodb.com/products/compass

2. **Connect:**
   - Paste your connection string
   - Click "Connect"

3. **Create Database:**
   - Click "Create Database"
   - Database name: `jenkins_failure_analysis`
   - Collection name: `builds`

4. **Create Collections:**
   - `builds`
   - `console_logs`
   - `test_results`
   - `analysis_solutions`
   - `refinement_history`

### Option B: Using Python Script

I'll create a script for you (see Step 8)

---

## Step 7: Update Your .env File

Edit `C:\DDN-AI-Project-Documentation\.env`:

```env
# ===================== MongoDB Atlas Configuration =====================

# REPLACE THIS with your actual connection string
MONGODB_URI=mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority

# Database name
MONGODB_DB=jenkins_failure_analysis

# ===================== Keep these if using local MongoDB =====================
# Comment out or remove if using Atlas only

# MONGODB_LOCAL_URI=mongodb://admin:password@mongodb:27017/
```

**Full example:**
```env
# AI & ML APIs
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
PINECONE_API_KEY=xxxxx

# MongoDB Atlas (Cloud)
MONGODB_URI=mongodb+srv://ddn_admin:MySecure123!Pass@ddn-ai-cluster.abc123.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=jenkins_failure_analysis

# GitHub
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO=your-org/your-repo

# Rest of your configuration...
```

---

## Step 8: Test Connection

### Create Test Script

Create file: `test-mongodb-atlas.py`

```python
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mongodb_atlas():
    """Test MongoDB Atlas connection"""

    # Get connection string from .env
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db = os.getenv('MONGODB_DB', 'jenkins_failure_analysis')

    if not mongodb_uri:
        print("❌ ERROR: MONGODB_URI not found in .env file")
        return False

    print("🔗 Connecting to MongoDB Atlas...")
    print(f"📦 Database: {mongodb_db}")

    try:
        # Create client with server API
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'))

        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")

        # Get database
        db = client[mongodb_db]

        # List collections
        collections = db.list_collection_names()
        print(f"\n📂 Collections in database '{mongodb_db}':")
        if collections:
            for col in collections:
                count = db[col].count_documents({})
                print(f"   - {col}: {count} documents")
        else:
            print("   (No collections yet)")

        # Create sample collections if they don't exist
        required_collections = [
            'builds',
            'console_logs',
            'test_results',
            'analysis_solutions',
            'refinement_history'
        ]

        print("\n📋 Creating required collections...")
        for col_name in required_collections:
            if col_name not in collections:
                db.create_collection(col_name)
                print(f"   ✅ Created: {col_name}")
            else:
                print(f"   ✓ Exists: {col_name}")

        # Insert test document
        print("\n🧪 Inserting test document...")
        test_collection = db['builds']
        test_doc = {
            'test': True,
            'message': 'MongoDB Atlas connection successful',
            'timestamp': '2025-10-22T00:00:00Z'
        }
        result = test_collection.insert_one(test_doc)
        print(f"   ✅ Test document inserted with ID: {result.inserted_id}")

        # Clean up test document
        test_collection.delete_one({'_id': result.inserted_id})
        print(f"   🧹 Test document cleaned up")

        print("\n✅ MongoDB Atlas is ready to use!")
        print(f"🌐 Connection string: {mongodb_uri[:50]}...")

        client.close()
        return True

    except Exception as e:
        print(f"\n❌ ERROR connecting to MongoDB Atlas:")
        print(f"   {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your connection string in .env")
        print("2. Verify password is URL-encoded")
        print("3. Check Network Access allows your IP (0.0.0.0/0)")
        print("4. Verify database user exists with correct password")
        return False

if __name__ == '__main__':
    test_mongodb_atlas()
```

### Run Test

```bash
cd C:\DDN-AI-Project-Documentation
python test-mongodb-atlas.py
```

**Expected output:**
```
🔗 Connecting to MongoDB Atlas...
📦 Database: jenkins_failure_analysis
✅ Connected to MongoDB Atlas successfully!

📂 Collections in database 'jenkins_failure_analysis':
   (No collections yet)

📋 Creating required collections...
   ✅ Created: builds
   ✅ Created: console_logs
   ✅ Created: test_results
   ✅ Created: analysis_solutions
   ✅ Created: refinement_history

🧪 Inserting test document...
   ✅ Test document inserted with ID: 67xxxxx
   🧹 Test document cleaned up

✅ MongoDB Atlas is ready to use!
```

---

## Step 9: Update Docker Compose (Optional)

If using MongoDB Atlas, you can **remove** the local MongoDB service from `docker-compose.yml`:

### Option A: Comment Out Local MongoDB

```yaml
# Comment out the mongodb service since using Atlas
#  mongodb:
#    image: mongo:7.0
#    container_name: ddn-mongodb
#    ports:
#      - "27017:27017"
#    ...
```

### Option B: Keep Both (Flexible)

Keep local MongoDB for development, use Atlas for production:

```yaml
# Local MongoDB (development)
mongodb:
  image: mongo:7.0
  ...
  # Only start if needed: docker-compose up mongodb
```

Use environment variable to switch:

```env
# Development: use local
MONGODB_URI=mongodb://admin:password@mongodb:27017/

# Production: use Atlas
MONGODB_URI=mongodb+srv://ddn_admin:pass@cluster.mongodb.net/
```

---

## Step 10: Verify Services Connect to Atlas

### Update service environment variables

All services that use MongoDB should use Atlas connection:

```yaml
# In docker-compose.yml
langgraph-service:
  environment:
    - MONGODB_URI=${MONGODB_URI}  # Uses .env value (Atlas)
    - MONGODB_DB=${MONGODB_DB}

dashboard-api:
  environment:
    - MONGODB_URI=${MONGODB_URI}  # Uses .env value (Atlas)
    - MONGODB_DB=${MONGODB_DB}
```

This is **already configured** in your docker-compose.yml!

---

## Step 11: Start Your System with Atlas

### Start Services

```bash
cd C:\DDN-AI-Project-Documentation

# Start all services (using Atlas for MongoDB)
docker-compose up -d

# Check logs
docker-compose logs -f langgraph-service
docker-compose logs -f dashboard-api
```

**Expected in logs:**
```
Connected to MongoDB: jenkins_failure_analysis
Using MongoDB Atlas
```

---

## Getting Your Connection String from Atlas

### Quick Steps:

1. **Login:** https://cloud.mongodb.com/
2. **Clusters:** Click "Database" in left sidebar
3. **Connect:** Click "Connect" button on your cluster
4. **Method:** Choose "Connect your application"
5. **Copy:** Connection string shown
6. **Modify:** Replace `<password>` with actual password
7. **Paste:** Into `.env` file as `MONGODB_URI`

---

## Connection String Examples

### Basic Format
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?options
```

### Your Format (from your account)
```
mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-ai-cluster.xxxxx.mongodb.net/jenkins_failure_analysis?retryWrites=true&w=majority
```

### With Database Name
```
mongodb+srv://ddn_admin:pass@cluster.abc123.mongodb.net/jenkins_failure_analysis?retryWrites=true&w=majority
```

### With Options
```
mongodb+srv://ddn_admin:pass@cluster.mongodb.net/jenkins_failure_analysis?retryWrites=true&w=majority&appName=DDN-AI
```

---

## Troubleshooting

### Error: "Authentication failed"

**Solution:**
1. Check username and password are correct
2. URL-encode special characters in password
3. Verify user exists in "Database Access"

### Error: "Connection timeout"

**Solution:**
1. Check "Network Access" allows your IP
2. Add `0.0.0.0/0` to allow from anywhere
3. Wait 2-3 minutes after adding IP

### Error: "Database not found"

**Solution:**
- Database is created automatically on first write
- Or create manually in Atlas UI
- Connection string can include database name

### Error: "SSL/TLS connection error"

**Solution:**
1. Ensure using `mongodb+srv://` (not `mongodb://`)
2. Update Python driver: `pip install --upgrade pymongo`
3. Use `&tls=true` in connection string

---

## Best Practices

### Security

✅ **Use strong passwords** - Mix of letters, numbers, symbols
✅ **Rotate credentials** - Change passwords regularly
✅ **Limit IP access** - Only allow needed IPs
✅ **Use environment variables** - Never hardcode credentials
✅ **Enable audit logs** - Track database access

### Performance

✅ **Create indexes** - On frequently queried fields
✅ **Connection pooling** - Already handled by PyMongo
✅ **Monitor usage** - Check Atlas metrics
✅ **Use appropriate read/write concerns**

### Cost Management

✅ **Start with M0 free tier** - 512MB storage
✅ **Monitor data size** - Check Atlas dashboard
✅ **Set up alerts** - Get notified before limits
✅ **Upgrade when needed** - M10 starts at $0.08/hr

---

## MongoDB Atlas Features You Get

✅ **Automatic backups** - Point-in-time recovery
✅ **Performance monitoring** - Real-time metrics
✅ **Alerts** - Email notifications
✅ **Global deployment** - Multi-region
✅ **Search indexes** - Full-text search
✅ **Charts** - Data visualization
✅ **Realm** - Serverless functions

---

## Quick Reference Commands

### Test Connection
```bash
python test-mongodb-atlas.py
```

### View Data (MongoDB Compass)
```
1. Download: https://www.mongodb.com/products/compass
2. Connect with your connection string
3. Browse databases and collections
```

### View Data (Python)
```python
from pymongo import MongoClient
client = MongoClient('your-connection-string')
db = client['jenkins_failure_analysis']
print(list(db.builds.find()))
```

### Backup Database
```
Atlas does this automatically!
Backups → Configure → Enable continuous backups
```

---

## Summary Checklist

After completing this guide, you should have:

✅ MongoDB Atlas account accessed
✅ Cluster created (or existing one used)
✅ Database user created with password
✅ Network access configured (0.0.0.0/0 or your IP)
✅ Connection string obtained
✅ .env file updated with MONGODB_URI
✅ Collections created in database
✅ Connection tested successfully
✅ Services updated to use Atlas
✅ System running with cloud MongoDB

---

## Next Steps

1. **Start your services:**
   ```bash
   docker-compose up -d
   ```

2. **Import n8n workflows:**
   - Configure MongoDB credentials in n8n
   - Use Atlas connection string

3. **Test the system:**
   - Trigger manual analysis
   - Check data in Atlas dashboard

4. **Monitor usage:**
   - Atlas dashboard shows storage and operations
   - Set up alerts for limits

---

## Support

**MongoDB Atlas Docs:**
- https://docs.atlas.mongodb.com/

**Connection Strings:**
- https://docs.mongodb.com/manual/reference/connection-string/

**Python Driver:**
- https://pymongo.readthedocs.io/

**DDN AI Documentation:**
- [START-HERE.md](START-HERE.md)
- [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)

---

**Last Updated:** October 22, 2025
**Status:** Production Ready ✅
