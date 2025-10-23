# RAG Data Sources - Complete Explanation

**Document**: Detailed explanation of all data sources for RAG system
**Diagram**: `RAG-Technical-Deep-Dive.jpg` (Updated: 2.8MB, 9600x7200px)
**Date**: October 21, 2025
**Status**: Production Documentation

---

## 📊 Diagram Updates

### **What's New:**
- ✅ **NO overlapping labels** - Improved spacing and layout
- ✅ **8 Data Sources** shown in detail
- ✅ **4 Database layers** explained
- ✅ **Complete data flow** from source to output
- ✅ **Feedback loop** clearly marked
- ✅ **Historical data** section highlighted

---

## 🗂️ Complete Data Sources (8 Sources)

### **1. Console Logs**

**What it contains:**
```
Full build output from Jenkins
├── Compilation output
├── Test execution logs
├── Error stack traces
├── Warning messages
├── Debug statements
└── System.out.println() outputs
```

**Example:**
```
[INFO] Building DDN Storage Module 1.0.0
[INFO] Compiling 47 source files
[ERROR] OutOfMemoryError: Java heap space
    at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127)
    at com.ddn.tests.StorageTest.testInit(StorageTest.java:45)
[ERROR] BUILD FAILURE
```

**Source**: Jenkins console output
**Format**: Plain text log file
**Size**: Up to 10MB per build
**Storage**: MongoDB (`console_logs` collection)

**Used for:**
- Identifying error messages
- Finding stack traces
- Understanding error context
- Debugging information

---

### **2. XML Reports (JUnit/TestNG)**

**What it contains:**
```
Test execution results in XML format
├── Test suite name
├── Test case names
├── Pass/Fail status
├── Assertion failures
├── Test duration
├── Error details
└── System properties
```

**Example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="StorageTests" tests="15" failures="3" errors="1" time="45.2">
  <testcase name="testInitialization" classname="com.ddn.tests.StorageTest" time="2.1">
    <error message="OutOfMemoryError: Java heap space" type="java.lang.OutOfMemoryError">
      <![CDATA[
      java.lang.OutOfMemoryError: Java heap space
        at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127)
      ]]>
    </error>
  </testcase>
  <testcase name="testWrite" classname="com.ddn.tests.StorageTest" time="1.5">
    <failure message="Expected 100 but was 0" type="org.junit.AssertionError">
      Expected 100 but was 0
    </failure>
  </testcase>
</testsuite>
```

**Source**: Test runner (JUnit, TestNG, pytest)
**Format**: XML (JUnit format)
**Size**: 1-5MB per build
**Storage**: MongoDB (`test_results` collection)

**Used for:**
- Identifying which tests failed
- Understanding assertion failures
- Test duration analysis
- Test coverage metrics

---

### **3. Debug Reports**

**What it contains:**
```
JVM and application debug information
├── Thread dumps
├── Heap dumps
├── Garbage collection logs
├── Memory usage statistics
├── CPU profiling data
└── Performance metrics
```

**Example (Thread Dump):**
```
"main" #1 prio=5 os_prio=0 tid=0x00007f8c8000a800 nid=0x1234 runnable [0x00007f8c8e123000]
   java.lang.Thread.State: RUNNABLE
        at com.ddn.storage.DDNStorage.allocate(DDNStorage.java:127)
        at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:89)

"GC Thread" #2 daemon prio=9 os_prio=0 tid=0x00007f8c8001a000 nid=0x1235 runnable

Heap:
 PSYoungGen      total 76288K, used 76288K [0x000000076ab00000, 0x0000000770000000, 0x00000007c0000000)
  eden space 65536K, 100% used [0x000000076ab00000,0x000000076eb00000,0x000000076eb00000)
 ParOldGen       total 175104K, used 175103K [0x00000006c0000000, 0x00000006cab00000, 0x000000076ab00000)
  object space 175104K, 99% used [0x00000006c0000000,0x00000006caaffc78,0x00000006cab00000)
```

**Source**: JVM, application instrumentation
**Format**: Plain text, binary dumps
**Size**: 10-500MB (heap dumps can be large)
**Storage**: MongoDB (`debug_reports` collection) - only metadata, full dumps in file storage

**Used for:**
- Memory leak detection
- Thread deadlock analysis
- Heap usage patterns
- GC performance issues

---

### **4. System Metadata**

**What it contains:**
```
Build environment and system information
├── OS information (Linux, Windows, macOS)
├── Java version (OpenJDK 11, 17, etc.)
├── Maven/Gradle version
├── Dependency versions
├── Environment variables
├── Build parameters
├── Resource usage (CPU, RAM)
└── Network configuration
```

**Example:**
```json
{
  "os": {
    "name": "Linux",
    "version": "Ubuntu 20.04.3 LTS",
    "arch": "amd64"
  },
  "java": {
    "version": "11.0.12",
    "vendor": "OpenJDK",
    "home": "/usr/lib/jvm/java-11-openjdk"
  },
  "maven": {
    "version": "3.8.1",
    "java_home": "/usr/lib/jvm/java-11-openjdk"
  },
  "resources": {
    "max_memory": "2048M",
    "available_processors": 4,
    "free_memory": "124M",
    "total_memory": "2048M"
  },
  "dependencies": {
    "junit": "4.13.2",
    "spring-boot": "2.5.4",
    "ddn-sdk": "1.2.3"
  }
}
```

**Source**: Jenkins API, build system
**Format**: JSON
**Size**: < 100KB per build
**Storage**: MongoDB (`system_info` collection)

**Used for:**
- Identifying environment-specific issues
- Dependency conflict detection
- Resource constraint analysis
- Compatibility checking

---

### **5. GitHub Context**

**What it contains:**
```
Git commit and code information
├── Commit SHA
├── Commit message
├── Author information
├── Changed files (diff)
├── Branch name
├── Pull request info
├── Recent commit history
└── File contents
```

**Example:**
```json
{
  "commit": {
    "sha": "a1b2c3d4e5f6g7h8i9j0",
    "message": "Optimize DDN storage initialization",
    "author": {
      "name": "John Doe",
      "email": "john.doe@company.com",
      "date": "2025-10-21T10:00:00Z"
    },
    "branch": "feature/ddn-storage-optimization"
  },
  "changed_files": [
    {
      "filename": "src/main/java/com/ddn/storage/DDNStorage.java",
      "status": "modified",
      "additions": 25,
      "deletions": 10,
      "patch": "@@ -120,7 +120,8 @@ public class DDNStorage {\n..."
    }
  ],
  "file_contents": {
    "DDNStorage.java": "package com.ddn.storage;\n\npublic class DDNStorage {\n    public void initialize() {\n        // Allocate memory for storage\n        byte[] buffer = new byte[1024 * 1024 * 1024]; // 1GB\n    }\n}"
  }
}
```

**Source**: GitHub API
**Format**: JSON
**Size**: 100KB - 5MB per build (depending on changed files)
**Storage**: MongoDB (`github_context` collection)

**Used for:**
- Understanding what changed in the code
- Identifying code-related errors
- Providing context for MCP analysis
- Tracking who made the change

---

### **6. Knowledge Documents**

**What it contains:**
```
Project documentation and guides
├── README.md
├── Architecture documentation
├── Setup guides
├── Troubleshooting guides
├── API documentation
├── Configuration examples
└── Best practices
```

**Example (README.md snippet):**
```markdown
# DDN Storage Module

## Common Issues

### OutOfMemoryError

**Symptom:** Build fails with `java.lang.OutOfMemoryError: Java heap space`

**Cause:** JVM heap size is insufficient for DDN storage initialization

**Solution:**
1. Increase JVM heap size to at least 4GB
2. Add `-Xmx4g` to JAVA_OPTS
3. For large datasets, use `-Xmx8g`

**Configuration:**
```bash
export JAVA_OPTS="-Xms2g -Xmx4g"
mvn clean install
```

**Prevention:**
- Set minimum heap in Jenkins job configuration
- Monitor heap usage with JVisualVM
```

**Source**: Git repository (docs/ folder, README files)
**Format**: Markdown, plain text
**Size**: 10KB - 1MB total
**Storage**: MongoDB (`knowledge_docs` collection)

**Used for:**
- Providing context about error types
- Finding known solutions
- Understanding project architecture
- Quick reference for common issues

---

### **7. Error Catalog (Error Type Database)**

**What it contains:**
```
Predefined error type definitions and patterns
├── Error type mappings
├── Keyword → Category rules
├── Known error patterns
├── Common solutions
├── Error severity levels
└── Classification rules
```

**Example:**
```json
{
  "error_types": {
    "INFRA_ERROR": {
      "keywords": [
        "outofmemoryerror",
        "heap space",
        "disk space",
        "connection refused",
        "timeout",
        "resource exhausted"
      ],
      "severity": "HIGH",
      "typical_solutions": [
        "Increase resource allocation",
        "Check system limits",
        "Optimize resource usage"
      ],
      "examples": [
        "java.lang.OutOfMemoryError: Java heap space",
        "java.lang.OutOfMemoryError: Metaspace",
        "No space left on device"
      ]
    },
    "CODE_ERROR": {
      "keywords": [
        "nullpointerexception",
        "arrayindexoutofboundsexception",
        "classnotfoundexception",
        "illegalargumentexception"
      ],
      "severity": "MEDIUM",
      "typical_solutions": [
        "Review code logic",
        "Add null checks",
        "Verify array bounds"
      ]
    },
    "CONFIG_ERROR": {
      "keywords": [
        "permission denied",
        "configuration error",
        "invalid configuration",
        "missing property"
      ],
      "severity": "LOW",
      "typical_solutions": [
        "Check configuration files",
        "Verify file permissions",
        "Review environment variables"
      ]
    }
  }
}
```

**Source**: Knowledge base (manually curated)
**Format**: JSON
**Size**: < 1MB
**Storage**: In-memory cache, MongoDB backup

**Used for:**
- Fast error classification (no AI needed)
- Keyword-based categorization
- Understanding error severity
- Initial routing (RAG vs MCP)

---

### **8. Historical Data (RAG Source)**

**What it contains:**
```
Past build failures and their solutions
├── Previous error messages
├── Proven solutions (that worked)
├── Success rates
├── Usage counts
├── Similarity patterns
└── Embeddings
```

**Example:**
```json
{
  "vector_id": "BUILD_11000_1729584000",
  "embedding": [0.234, -0.567, 0.123, ..., 0.789],  // 1536 dimensions
  "metadata": {
    "build_id": "BUILD_11000",
    "error_text": "java.lang.OutOfMemoryError: Java heap space at com.ddn.storage.DDNStorage.initialize",
    "error_category": "INFRA_ERROR",
    "root_cause": "JVM heap size insufficient for DDN storage initialization",
    "solution": "Increase JVM heap size to 4GB using -Xmx4g flag",
    "fix_command": "export JAVA_OPTS='-Xms2g -Xmx4g'",
    "prevention": "Set minimum heap for all DDN builds in Jenkins configuration",
    "success_rate": 0.92,  // Worked 23 out of 25 times
    "times_used": 25,
    "times_successful": 23,
    "times_failed": 2,
    "confidence": 0.95,
    "first_seen": "2025-09-15T10:00:00Z",
    "last_used": "2025-10-19T15:30:00Z",
    "avg_fix_time_minutes": 15,
    "similar_builds": ["BUILD_10500", "BUILD_9800", "BUILD_8900"]
  }
}
```

**Source**: Pinecone vector database + MongoDB
**Format**: Vector embeddings + JSON metadata
**Size**:
- Pinecone: 1536 floats per error (~6KB per vector)
- MongoDB: Full solution details (up to 40KB per solution)
**Storage**:
- **Pinecone**: Vector embeddings and small metadata
- **MongoDB**: Complete solution details

**Used for:**
- Finding similar past errors
- Retrieving proven solutions
- Calculating success rates
- Learning from history

**Key Metrics:**
- Current errors stored: ~1,000
- Growth rate: ~10 new errors/month
- RAG hit rate: 80% (800 out of 1,000 queries)
- Average similarity score: 0.91

---

## 🗄️ Database Storage Layer (4 Databases)

### **1. PostgreSQL (Relational Database)**

**What it stores:**
```sql
-- Build metadata table
CREATE TABLE builds (
    build_id VARCHAR(50) PRIMARY KEY,
    build_number INT,
    job_name VARCHAR(200),
    status VARCHAR(20),  -- FAILURE, SUCCESS
    branch VARCHAR(100),
    commit_sha VARCHAR(40),
    created_at TIMESTAMP,
    aging_status VARCHAR(20),  -- PENDING, READY_FOR_ANALYSIS
    aging_days INT DEFAULT 0,
    analysis_status VARCHAR(30),  -- NOT_ANALYZED, ANALYZING, ANALYZED
    analyzed_at TIMESTAMP,
    analysis_type VARCHAR(20)  -- RAG, MCP
);

-- Analysis results table
CREATE TABLE failure_analysis (
    id SERIAL PRIMARY KEY,
    build_id VARCHAR(50) REFERENCES builds(build_id),
    error_category VARCHAR(50),
    root_cause TEXT,
    fix_recommendation TEXT,
    confidence_score DECIMAL(3,2),
    success_rate DECIMAL(3,2),
    times_used INT,
    created_at TIMESTAMP
);

-- User feedback table
CREATE TABLE user_feedback (
    id SERIAL PRIMARY KEY,
    analysis_id INT REFERENCES failure_analysis(id),
    feedback_type VARCHAR(20),  -- success, failed, partial
    feedback_text TEXT,
    user_id VARCHAR(100),
    submitted_at TIMESTAMP
);
```

**Purpose:**
- Quick queries for build status
- Aging criteria tracking
- Relational data (foreign keys)
- ACID transactions

**Performance:**
- Fast queries (< 10ms)
- Indexed columns for quick lookups
- ~10,000 builds stored

---

### **2. MongoDB (Document Database)**

**Collections:**

```javascript
// console_logs collection
{
  "_id": ObjectId("..."),
  "build_id": "BUILD_12345",
  "log": "Full console output text...",  // Up to 10MB
  "lines": 5000,
  "created_at": ISODate("2025-10-21T10:00:00Z")
}

// test_results collection
{
  "_id": ObjectId("..."),
  "build_id": "BUILD_12345",
  "xml_content": "<testsuite>...</testsuite>",
  "parsed_results": {
    "total_tests": 15,
    "failures": 3,
    "errors": 1,
    "duration": 45.2,
    "failed_tests": [...]
  }
}

// github_context collection
{
  "_id": ObjectId("..."),
  "build_id": "BUILD_12345",
  "commit": { ... },
  "changed_files": [ ... ],
  "file_contents": { ... }
}

// knowledge_docs collection
{
  "_id": ObjectId("..."),
  "filename": "README.md",
  "content": "# DDN Storage Module...",
  "category": "setup_guide",
  "last_updated": ISODate("2025-10-01T00:00:00Z")
}

// analysis_solutions collection
{
  "_id": ObjectId("..."),
  "build_id": "BUILD_12345",
  "analysis_type": "RAG_HISTORICAL_SOLUTION",
  "root_cause": "JVM heap insufficient",
  "solution": "Increase heap to 4GB",
  "success_rate": 0.92,
  "similar_build_ids": ["BUILD_11000", ...]
}
```

**Purpose:**
- Store large, unstructured data
- Flexible schema (JSON documents)
- Fast document retrieval
- Full-text search capabilities

**Performance:**
- Fast document queries (< 50ms)
- Large document support (up to 16MB)
- ~10,000 documents across collections

---

### **3. Pinecone (Vector Database)**

**Index Structure:**
```python
# Index configuration
{
  "name": "ddn-error-solutions",
  "dimension": 1536,  # Must match OpenAI embedding model
  "metric": "cosine",  # For similarity search
  "pod_type": "s1",  # Serverless
  "environment": "us-east-1-aws"
}

# Vector entry
{
  "id": "BUILD_12345_1729584000",
  "values": [0.234, -0.567, ..., 0.789],  # 1536 floats
  "metadata": {
    "build_id": "BUILD_12345",
    "error_category": "INFRA_ERROR",
    "root_cause": "JVM heap insufficient",
    "solution": "Increase heap to 4GB",
    "success_rate": 0.92,
    "times_used": 25,
    "confidence": 0.95,
    "timestamp": "2025-10-21T10:00:00Z"
  }
}
```

**Purpose:**
- Fast similarity search (< 300ms)
- Semantic search (meaning-based)
- Scalable to millions of vectors
- Filtered queries (by category)

**Performance:**
- Query time: 300ms for top 5 results
- Accuracy: 99% recall at 0.85 similarity
- Capacity: 100,000 vectors (free tier)
- Current usage: ~1,000 vectors

---

### **4. Knowledge Index (In-Memory Cache)**

**Structure:**
```javascript
// In-memory data structure (Python dict)
knowledge_index = {
  "error_patterns": {
    "INFRA_ERROR": [
      r"outofmemoryerror",
      r"heap space",
      r"disk\s+space",
      r"connection\s+refused"
    ],
    "CODE_ERROR": [
      r"nullpointerexception",
      r"arrayindexoutofboundsexception"
    ],
    // ...
  },
  "severity_rules": {
    "CRITICAL": ["outofmemoryerror", "fatal"],
    "HIGH": ["error", "exception"],
    "MEDIUM": ["warning", "deprecated"],
    "LOW": ["info", "debug"]
  },
  "quick_solutions": {
    "outofmemoryerror": "Increase JVM heap size",
    "permission denied": "Check file permissions",
    "module not found": "Install missing dependency"
  }
}
```

**Purpose:**
- Ultra-fast keyword matching (< 10ms)
- No database query needed
- Simple pattern matching
- Loaded at startup

**Performance:**
- Lookup time: < 10ms
- Memory usage: < 1MB
- Regex compilation: Done at startup

---

## 🔄 Complete Data Flow

### **Step 1: Build Fails (T+0)**
```
Jenkins Build #12345 fails
    ↓
Jenkins triggers post-build script
    ↓
Script collects data from 8 sources:
    1. Console logs → Captured from Jenkins
    2. XML reports → From test runner output
    3. Debug reports → From JVM flags
    4. System metadata → From Jenkins API
    5. GitHub context → From GitHub API
    6. Knowledge docs → From repository
    7. Error catalog → From knowledge base
    8. (Historical data used later in RAG step)
```

### **Step 2: Store in Databases (T+5 seconds)**
```
PostgreSQL ← Build metadata (ID, status, timestamps)
MongoDB ← All large data (logs, XML, code, docs)
Knowledge Index ← Already in memory (loaded at startup)
Pinecone ← No data yet (will be added after analysis)
```

### **Step 3: Wait or Trigger (T+0 to 3 days)**
```
Option A: Wait 3 days (automatic aging)
Option B: Manual trigger from dashboard (immediate)
    ↓
Trigger n8n webhook
```

### **Step 4: RAG Processing (T+0 to 5 seconds)**

```
4a. Fetch Data (100ms)
    MongoDB.find({"build_id": "BUILD_12345"})
    → Get console logs, XML, debug, GitHub, knowledge

4b. Classify Error (50ms)
    Knowledge Index.match(error_text)
    → Category: INFRA_ERROR
    → Confidence: 0.95

4c. Generate Embedding (200ms)
    OpenAI.create_embedding(error_text)
    → Output: [1536 floats]

4d. Search Pinecone (300ms)
    Pinecone.query(
        vector=embedding,
        filter={"error_category": "INFRA_ERROR"},
        top_k=5
    )
    → Results: 5 similar errors with scores

4e. Retrieve Solution (50ms)
    Best match: Similarity 0.95, Success rate 0.92
    → Root cause: "JVM heap insufficient"
    → Solution: "Increase heap to 4GB"

4f. Decision (10ms)
    IF similarity > 0.85 AND success_rate > 0.80:
        → Use RAG solution ✓
    ELSE:
        → Use MCP deep analysis
```

### **Step 5: Output (T+200ms)**
```
Store in MongoDB:
    analysis_solutions collection
    → Complete solution with metadata

Update Pinecone:
    Store new embedding (if new solution)
    OR
    Increment usage count (if existing solution)

Update PostgreSQL:
    builds.analysis_status = "ANALYZED"
    builds.analysis_type = "RAG"

Send Notifications:
    Teams → Solution summary
    Dashboard → Clickable links
```

### **Step 6: Feedback Loop (ongoing)**
```
User tests solution:
    ✓ Worked → feedback_type = "success"
    ✗ Failed → feedback_type = "failed"

Update Pinecone:
    IF success:
        success_rate = (times_successful + 1) / (times_used + 1)
        times_successful++
        times_used++
    ELSE:
        success_rate = times_successful / (times_used + 1)
        times_used++

Future queries benefit from updated success_rate!
```

---

## 📊 Data Source Usage in RAG Pipeline

| Data Source | Used in Classification | Used in RAG Search | Used in MCP Analysis | Storage Location |
|-------------|----------------------|-------------------|---------------------|------------------|
| **Console Logs** | ✓ (error text extraction) | ✓ (embedding generation) | ✓ (context) | MongoDB |
| **XML Reports** | ✓ (test failure detection) | ✗ | ✓ (test context) | MongoDB |
| **Debug Reports** | ✗ | ✗ | ✓ (deep analysis) | MongoDB |
| **System Metadata** | ✓ (environment checking) | ✗ | ✓ (compatibility) | MongoDB |
| **GitHub Context** | ✗ | ✗ | ✓ (code analysis) | MongoDB |
| **Knowledge Docs** | ✓ (known issues check) | ✓ (context enrichment) | ✓ (reference) | MongoDB |
| **Error Catalog** | ✓ ✓ ✓ (keyword matching) | ✓ (category filter) | ✓ (classification) | In-Memory |
| **Historical Data** | ✗ | ✓ ✓ ✓ (main RAG source) | ✗ | Pinecone + MongoDB |

---

## 🎯 Key Insights

### **Why 8 Data Sources?**

1. **Comprehensive Context**: Each source provides different information
2. **Redundancy**: If one source fails, others provide fallback
3. **Accuracy**: More data = better error classification
4. **Coverage**: Different error types need different sources

### **Data Source Priorities:**

**For INFRA_ERROR (80% of cases):**
1. Console logs (error message)
2. Historical data (past solutions)
3. Knowledge docs (known issues)

**For CODE_ERROR (20% of cases):**
1. Console logs (stack trace)
2. GitHub context (code changes)
3. Debug reports (heap dumps)
4. XML reports (test failures)

### **Storage Strategy:**

- **Hot data** (frequently accessed): Pinecone, In-Memory
- **Warm data** (occasionally accessed): MongoDB
- **Cold data** (rarely accessed): PostgreSQL, File storage

### **Performance Optimization:**

- Knowledge Index cached in memory → 10ms lookup
- Pinecone indexed by category → 300ms search (not 3 seconds)
- MongoDB compound indexes → 50ms query (not 500ms)
- PostgreSQL indexed columns → 10ms query

---

## ✅ Summary

**Data Sources:**
- ✅ 8 comprehensive sources covering all error types
- ✅ Console logs, XML, debug, system, GitHub, knowledge, catalog, historical

**Storage:**
- ✅ 4 database layers for different data types
- ✅ PostgreSQL (metadata), MongoDB (documents), Pinecone (vectors), In-Memory (cache)

**Flow:**
- ✅ Complete data pipeline from error to solution
- ✅ 5-second RAG analysis (vs 18-second Claude AI)
- ✅ Feedback loop for continuous learning

**Coverage:**
- ✅ 80% of errors handled by RAG
- ✅ 20% require deep MCP analysis
- ✅ Historical data grows over time

---

**The comprehensive diagram (`RAG-Technical-Deep-Dive.jpg`) now shows all of this in visual form!**
