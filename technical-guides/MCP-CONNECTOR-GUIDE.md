# MCP Connector Complete Guide - DDN Project

**What**: Model Context Protocol - A standardized way for Claude AI to use external tools
**Why**: Enable intelligent, autonomous decision-making instead of fixed workflows
**When**: Use for code analysis and selective database queries

---

## 🎯 Why MCP is Essential for DDN Project

### **Problem Without MCP:**

Your current Workflow 122 has **40+ HTTP nodes** that:
- ❌ Always execute ALL endpoints (even irrelevant ones)
- ❌ Fetch ALL data upfront (wastes time, money, tokens)
- ❌ Cannot make dynamic decisions based on error type
- ❌ Gemini receives pre-processed data (cannot ask for more info)

**Result**: 3-5 minutes per analysis, 50,000+ tokens, high cost

---

### **Solution With MCP:**

```
Single n8n node → Claude with MCP Connector
                     ↓
           Claude decides what to fetch
                     ↓
   Only calls relevant MCP tools (2-5 instead of 40+)
```

**Result**: 15-30 seconds per analysis, 3,000-8,000 tokens, 95% cost reduction

---

## 📚 MCP Concepts

### **1. What is MCP?**

MCP (Model Context Protocol) is a protocol that allows AI models to:
- Discover available tools
- Decide which tools to use
- Call tools autonomously
- Process tool results
- Make follow-up tool calls if needed

Think of it as: **"Giving Claude hands to interact with your systems"**

---

### **2. MCP Components**

```
┌──────────────────────────────────────────────────────────┐
│                    MCP ARCHITECTURE                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  n8n Workflow                                            │
│  └─ HTTP Request to Claude API                           │
│     └─ Headers: anthropic-beta: mcp-client-2025-04-04   │
│     └─ Body: {                                           │
│          "mcp_servers": [                                │
│            {                                             │
│              "type": "url",                              │
│              "url": "http://your-server:5000/sse",       │
│              "name": "mongodb-tools"                     │
│            },                                            │
│            {                                             │
│              "type": "url",                              │
│              "url": "http://your-server:5001/sse",       │
│              "name": "github-tools"                      │
│            }                                             │
│          ],                                              │
│          "messages": [...]                               │
│        }                                                 │
│                                                           │
│  ↓                                                        │
│                                                           │
│  Claude AI (Anthropic)                                   │
│  ├─ Reads error description                             │
│  ├─ Sees available tools from MCP servers                │
│  ├─ Decides: "I need console log from MongoDB"          │
│  ├─ Calls: mongodb_get_console_log(build_id)            │
│  ├─ Analyzes result                                     │
│  ├─ Decides: "I need code from GitHub"                  │
│  ├─ Calls: github_get_file(repo, path)                  │
│  └─ Returns: Final analysis                             │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ MCP Servers for DDN Project

### **MCP Server 1: MongoDB Tools**

**Purpose**: Query database only when Claude needs specific data

**File**: `C:\DDN-AI-Project-Documentation\mcp-configs\mongodb-mcp-server.py`

**Available Tools**:

1. **mongodb_get_full_error_details**
   - Input: `{build_id: "12345"}`
   - Returns: Complete stack trace, error context
   - When used: CODE_ERROR or TEST_FAILURE

2. **mongodb_get_console_log**
   - Input: `{build_id: "12345"}`
   - Returns: Full console output
   - When used: Any error type (if Claude needs it)

3. **mongodb_get_test_results**
   - Input: `{build_id: "12345"}`
   - Returns: Test execution data
   - When used: TEST_FAILURE

4. **mongodb_get_system_info**
   - Input: `{build_id: "12345"}`
   - Returns: System configuration
   - When used: INFRA_ERROR

---

### **MCP Server 2: GitHub Tools**

**Purpose**: Fetch source code only for code-related errors

**File**: `C:\DDN-AI-Project-Documentation\mcp-configs\github-mcp-server.py`

**Available Tools**:

1. **github_get_file**
   - Input: `{repo: "ddn-repo", file_path: "DDNStorage.java", start_line: 120, end_line: 135}`
   - Returns: Source code snippet
   - When used: CODE_ERROR

2. **github_get_blame**
   - Input: `{repo: "ddn-repo", file_path: "DDNStorage.java", line: 127}`
   - Returns: Who changed line 127, when, commit message
   - When used: To understand recent changes

3. **github_get_test_file**
   - Input: `{repo: "ddn-repo", test_name: "test_memory_usage"}`
   - Returns: Test source code
   - When used: TEST_FAILURE

---

## 🔄 How MCP Works in DDN Workflow

### **Example Flow: Infrastructure Error (NO MCP needed)**

```
1. n8n gets Jenkins webhook
   └─ Build #12345 failed: "OutOfMemoryError"

2. MongoDB query (minimal):
   └─ Get: build_id, error_log (first 500 chars), status

3. LangGraph classification:
   └─ Category: INFRA_ERROR
   └─ needs_code_analysis: FALSE
   └─ Similar solutions from RAG:
      - "Increase heap to 4GB"
      - "Add -Xmx4g flag"

4. Generate solution (NO Claude, NO MCP):
   └─ Use RAG solution directly

Result: 5 seconds, $0.01, NO MCP calls
```

---

### **Example Flow: Code Error (MCP needed)**

```
1. n8n gets Jenkins webhook
   └─ Build #12346 failed: "NullPointerException at DDNStorage.java:127"

2. MongoDB query (minimal):
   └─ Get: build_id, error_log, status

3. LangGraph classification:
   └─ Category: CODE_ERROR
   └─ needs_code_analysis: TRUE
   └─ File extracted: "DDNStorage.java"

4. n8n calls Claude with MCP:
   POST https://api.anthropic.com/v1/messages
   Headers:
     anthropic-version: 2023-06-01
     anthropic-beta: mcp-client-2025-04-04
     x-api-key: YOUR_KEY

   Body:
   {
     "model": "claude-3-5-sonnet-20241022",
     "max_tokens": 4096,
     "mcp_servers": [
       {
         "type": "url",
         "url": "http://localhost:5001/sse",
         "name": "mongodb-tools"
       },
       {
         "type": "url",
         "url": "http://localhost:5002/sse",
         "name": "github-tools"
       }
     ],
     "messages": [
       {
         "role": "user",
         "content": `Analyze this code error:

         Build ID: 12346
         Error: NullPointerException at DDNStorage.java:127

         You have access to:
         - mongodb-tools (to get full error details from database)
         - github-tools (to fetch source code)

         Steps:
         1. Use mongodb_get_full_error_details to get stack trace
         2. Use github_get_file to fetch DDNStorage.java around line 127
         3. Analyze and provide exact fix with code diff`
       }
     ]
   }

5. Claude's autonomous decision process:

   Step 1: "I need the full stack trace"
   → Calls MCP tool: mongodb_get_full_error_details(12346)
   → Receives: Complete stack trace

   Step 2: "I see the error is at line 127, let me get the code"
   → Calls MCP tool: github_get_file("ddn-repo", "DDNStorage.java", 120, 135)
   → Receives: Code lines 120-135

   Step 3: "I found the issue - missing null check"
   → Analyzes code
   → Generates fix:

   ```java
   // Current code (line 127):
   storageConfig.setData(data);

   // Fixed code:
   if (storageConfig == null) {
       throw new IllegalStateException("Storage not initialized");
   }
   storageConfig.setData(data);
   ```

6. Claude returns complete analysis

Result: 15 seconds, $0.08, 2 MCP calls (smart and selective)
```

---

## 📊 MCP vs Traditional Approach

| Aspect | Traditional (40+ nodes) | With MCP |
|--------|------------------------|----------|
| **API Calls** | 40+ (always) | 2-5 (dynamic) |
| **Data Fetched** | 50MB+ (everything) | 500KB (only needed) |
| **Execution Time** | 3-5 minutes | 15-30 seconds |
| **Token Usage** | 50,000+ | 3,000-8,000 |
| **Intelligence** | Fixed path | Autonomous decisions |
| **GitHub Access** | Every time | Only for code errors (20%) |
| **Cost per Run** | $0.75-$1.50 | $0.05-$0.15 |
| **Maintenance** | Update 40+ nodes | Update 2 MCP servers |

---

## 🔧 Setting Up MCP Servers

### **Step 1: Install Dependencies**

```bash
pip install flask anthropic pinecone-client pymongo requests python-dotenv
```

---

### **Step 2: Create MongoDB MCP Server**

See: `C:\DDN-AI-Project-Documentation\mcp-configs\mongodb-mcp-server.py`

```python
from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client['ddn']

@app.route('/sse')
def mcp_endpoint():
    """MCP Server endpoint"""
    # MCP protocol implementation
    pass

@app.route('/tools/mongodb_get_full_error_details', methods=['POST'])
def get_full_error_details():
    build_id = request.json.get('build_id')
    result = db.error_details.find_one({"build_id": build_id})
    return jsonify(result)

# ... more tool endpoints

if __name__ == '__main__':
    app.run(port=5001)
```

---

### **Step 3: Create GitHub MCP Server**

See: `C:\DDN-AI-Project-Documentation\mcp-configs\github-mcp-server.py`

```python
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "ddn/exascaler"

@app.route('/sse')
def mcp_endpoint():
    """MCP Server endpoint"""
    pass

@app.route('/tools/github_get_file', methods=['POST'])
def get_file():
    data = request.json
    file_path = data.get('file_path')
    start_line = data.get('start_line', 1)
    end_line = data.get('end_line', 9999)

    # Fetch from GitHub API
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    # Parse and return specific lines
    # ...
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5002)
```

---

### **Step 4: Configure n8n to Use MCP**

In your n8n workflow, replace 40+ nodes with:

**Single HTTP Request Node:**

```javascript
// Node: "Call Claude with MCP"

// URL
https://api.anthropic.com/v1/messages

// Method
POST

// Headers
{
  "x-api-key": "{{ $env.ANTHROPIC_API_KEY }}",
  "anthropic-version": "2023-06-01",
  "anthropic-beta": "mcp-client-2025-04-04",
  "content-type": "application/json"
}

// Body
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "mcp_servers": [
    {
      "type": "url",
      "url": "http://localhost:5001/sse",
      "name": "mongodb-tools",
      "authorization_token": "{{ $env.MONGODB_MCP_TOKEN }}"
    },
    {
      "type": "url",
      "url": "http://localhost:5002/sse",
      "name": "github-tools",
      "authorization_token": "{{ $env.GITHUB_MCP_TOKEN }}"
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": `Analyze build failure:

      Build ID: {{ $json.build_id }}
      Error: {{ $json.error_log }}
      Category: {{ $json.error_category }}

      You have access to mongodb-tools and github-tools.
      Investigate and provide root cause + fix recommendations.`
    }
  ]
}
```

---

## 🎓 Key Takeaways

1. **MCP = Autonomous Tool Usage**
   - Claude decides what to fetch (not pre-determined)

2. **80% of Errors Don't Need MCP**
   - Use RAG for infra/config/dependency errors
   - Save time and money

3. **20% of Errors Use MCP Intelligently**
   - Only fetch relevant MongoDB data
   - Only fetch specific GitHub files
   - Not entire database, not entire repo

4. **Massive Efficiency Gains**
   - 40+ API calls → 2-5 API calls
   - 3-5 minutes → 15-30 seconds
   - $1.50 → $0.15 per analysis

5. **Better AI Analysis**
   - Claude gets only relevant context
   - Can ask for more info if needed
   - Makes follow-up decisions autonomously

---

**Next Steps**:
- Review [MCP Server implementations](../mcp-configs/)
- Study [LangGraph integration](../implementation/LANGGRAPH-AGENT.md)
- Check [Best Practices](../best-practices/BEST-PRACTICES.md)

**Last Updated**: October 17, 2025
