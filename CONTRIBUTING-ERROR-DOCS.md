# 📝 Contributing to DDN Error Documentation

> **Purpose**: Enable team members to contribute high-quality error documentation to improve our RAG-powered AI analysis system.

**Version**: 1.0.0
**Last Updated**: 2025-11-05
**Maintainer**: DDN QA Team

---

## 🎯 Overview

The DDN Error Documentation system powers our AI-driven failure analysis by providing a searchable knowledge base of documented errors, root causes, and proven solutions. When you document an error, you're helping the AI provide better recommendations to the entire team.

### Current Status
- **30+ Errors Documented**: ERR001-ERR025 (and growing)
- **51-72% Similarity Matching**: RAG retrieval accuracy
- **6 Error Categories**: CODE, INFRASTRUCTURE, CONFIGURATION, DEPENDENCY, TEST, SECURITY
- **Fusion RAG System**: 4-source retrieval with re-ranking

---

## 📚 Table of Contents

1. [When to Document an Error](#when-to-document-an-error)
2. [Error Documentation Schema](#error-documentation-schema)
3. [Step-by-Step Contribution Process](#step-by-step-contribution-process)
4. [Field Requirements & Guidelines](#field-requirements--guidelines)
5. [Code Example Standards](#code-example-standards)
6. [Category Taxonomy](#category-taxonomy)
7. [Validation Checklist](#validation-checklist)
8. [Loading to Pinecone](#loading-to-pinecone)
9. [Examples from Existing Docs](#examples-from-existing-docs)
10. [Troubleshooting](#troubleshooting)

---

## 🔍 When to Document an Error

Document an error when:

✅ **It's recurring** - Seen in 3+ test runs or reported by multiple team members
✅ **Solution is non-obvious** - Took >30 minutes to debug or required deep investigation
✅ **It's environment-specific** - Related to DDN EXAScaler, AI400X, or specific infrastructure
✅ **Prevention is important** - Understanding root cause prevents future occurrences
✅ **Code fix is reusable** - Solution applies to similar scenarios

❌ **Don't document**:
- One-time flaky test failures with no clear pattern
- Simple typos or trivial fixes
- Errors already documented (check existing error-documentation.json first)
- Issues specific to local dev environment only

---

## 📋 Error Documentation Schema

### Complete JSON Structure

```json
{
  "error_id": "ERR###",
  "error_type": "ExceptionClassName or Error Type",
  "error_category": "CODE|INFRASTRUCTURE|CONFIGURATION|DEPENDENCY|TEST|SECURITY",
  "subcategory": "Specific classification",
  "error_message": "Complete error message as seen in logs",
  "component": "System component or service name",
  "file_path": "path/to/file.ext",
  "line_range": "125-135",
  "root_cause": "Detailed explanation of why the error occurs",
  "code_before": "Code snippet showing the problematic code",
  "code_after": "Code snippet showing the fixed code",
  "solution_steps": [
    "Step 1: Description",
    "Step 2: Description",
    "Step 3: Description"
  ],
  "prevention": "How to prevent this error in the future",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "frequency": "Common|Occasional|Rare description",
  "related_errors": ["ERR001", "ERR002"],
  "test_scenarios": ["Test scenario name 1", "Test scenario name 2"],
  "tags": ["tag1", "tag2", "tag3"]
}
```

---

## 🚀 Step-by-Step Contribution Process

### Step 1: Gather Information

When you encounter an error worth documenting:

1. **Capture the full error message** (including stack trace)
2. **Identify the failing component** (which service, module, or test)
3. **Document your investigation process** (what you checked, what you found)
4. **Record the solution** (code changes, configuration updates, commands run)
5. **Note prevention measures** (how to avoid in the future)

### Step 2: Assign Error ID

1. Check existing error documentation files:
   - `error-documentation.json` (ERR001-ERR010)
   - `error-documentation-phase2.json` (ERR011-ERR025)

2. Use the next sequential number:
   - If last error is ERR025, use ERR026
   - Format: `ERR###` (always 3 digits, zero-padded)

### Step 3: Create JSON Entry

Create your error documentation following the schema above. See [Field Requirements](#field-requirements--guidelines) for detailed field descriptions.

### Step 4: Choose Target File

**For major errors (HIGH/CRITICAL severity)**:
- Add to `error-documentation-phase2.json`
- These are production-critical issues

**For pattern documentation or batch additions**:
- Create a new phase file: `error-documentation-phase3.json`
- Follow the same structure

### Step 5: Validate JSON

Before submitting, validate your JSON:

```bash
# Use Python to validate
python -c "import json; json.load(open('error-documentation-phase2.json'))"

# Or use online validator: https://jsonlint.com/
```

### Step 6: Submit for Review

1. Create a feature branch: `git checkout -b error-docs/ERR###-short-description`
2. Add your changes: `git add error-documentation-phase2.json`
3. Commit with descriptive message:
   ```bash
   git commit -m "docs: Add ERR026 - CrossTenantAccessViolation documentation

   Documents multi-tenancy isolation error with code examples,
   solution steps, and prevention measures.

   Severity: CRITICAL
   Category: SECURITY"
   ```
4. Push and create Pull Request
5. Request review from @qa-team

### Step 7: Post-Merge Loading

After your PR is merged, load the documentation to Pinecone:

```bash
cd implementation
python load_error_docs_to_pinecone.py
```

See [Loading to Pinecone](#loading-to-pinecone) for details.

---

## 📝 Field Requirements & Guidelines

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `error_id` | String | Unique identifier (ERR###) | `"ERR026"` |
| `error_type` | String | Exception class or error type | `"NullPointerException"` |
| `error_category` | Enum | Primary category (see taxonomy) | `"CODE"` |
| `error_message` | String | Complete error message | `"java.lang.NullPointerException: Cannot invoke..."` |
| `root_cause` | String | Why the error occurs (100-500 words) | `"The storageConfig object is accessed without..."` |
| `code_before` | String | Problematic code (multiline) | See [Code Standards](#code-example-standards) |
| `code_after` | String | Fixed code (multiline) | See [Code Standards](#code-example-standards) |
| `solution_steps` | Array | Step-by-step fix instructions | `["Add null check", "Throw exception"]` |

### Recommended Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `subcategory` | String | Specific classification | `"Null Pointer Access"` |
| `component` | String | System component | `"DDN Storage Configuration"` |
| `file_path` | String | Relative file path | `"src/main/java/com/ddn/storage/DDNStorage.java"` |
| `line_range` | String | Line numbers | `"125-135"` |
| `prevention` | String | Prevention guidance (50-200 words) | `"Always validate object state..."` |
| `severity` | Enum | Impact level | `"HIGH"` |
| `frequency` | String | How often it occurs | `"Common in initialization flows"` |
| `related_errors` | Array | Related error IDs | `["ERR001", "ERR015"]` |
| `test_scenarios` | Array | Where error is seen | `["EXAScaler storage initialization"]` |
| `tags` | Array | Search keywords | `["null-pointer", "initialization", "storage-config"]` |

### Field Guidelines

#### error_type
- Use actual exception class name if applicable (e.g., `NullPointerException`, `ConnectionRefusedException`)
- For non-exception errors, use descriptive name (e.g., `DNSResolutionException`, `QuotaExceeded`)
- **Format**: PascalCase

#### error_message
- Include complete error message as it appears in logs
- Include relevant context (URLs, hostnames, ports)
- **Max Length**: 500 characters (truncate if longer, include "...")

#### root_cause
- Explain **why** the error occurs, not just what happened
- Include environmental conditions that trigger it
- Mention common scenarios
- **Length**: 100-500 words
- **Tone**: Technical but clear

#### solution_steps
- Minimum 3 steps, maximum 10
- Each step should be actionable
- Include commands where applicable
- Order chronologically
- **Format**: Array of strings, each 10-100 words

#### prevention
- Focus on **how to avoid** the error in the future
- Include best practices
- Mention code patterns, architectural considerations
- **Length**: 50-200 words

#### tags
- Use lowercase with hyphens: `"null-pointer"`, not `"NullPointer"`
- Include technology: `"lustre"`, `"s3"`, `"exascaler"`
- Include error type: `"connection-refused"`, `"403"`, `"timeout"`
- Include concepts: `"multi-tenancy"`, `"security"`, `"retry"`
- **Count**: 3-8 tags per error

---

## 💻 Code Example Standards

### General Principles

1. **Minimal but Complete** - Show enough context to understand the problem
2. **Self-Contained** - Should compile/run (or clearly show why it doesn't)
3. **Annotated** - Include comments explaining the issue
4. **Realistic** - Use actual code patterns from the project

### Language-Specific Formatting

#### Java

```json
"code_before": "public class LustreClient {\n    private String endpoint = \"http://exascaler.ddn.local:8080\";\n    \n    public Response getHealth() {\n        // No retry or timeout configuration\n        HttpClient client = HttpClient.newHttpClient();\n        HttpRequest request = HttpRequest.newBuilder()\n            .uri(URI.create(endpoint + \"/api/v1/health\"))\n            .build();\n        return client.send(request, HttpResponse.BodyHandlers.ofString());\n    }\n}",

"code_after": "public class LustreClient {\n    private String endpoint = \"http://exascaler.ddn.local:8080\";\n    private static final int MAX_RETRIES = 3;\n    private static final int TIMEOUT_SECONDS = 10;\n    \n    public Response getHealth() {\n        HttpClient client = HttpClient.newBuilder()\n            .connectTimeout(Duration.ofSeconds(TIMEOUT_SECONDS))\n            .build();\n        \n        for (int retry = 0; retry < MAX_RETRIES; retry++) {\n            try {\n                HttpRequest request = HttpRequest.newBuilder()\n                    .uri(URI.create(endpoint + \"/api/v1/health\"))\n                    .timeout(Duration.ofSeconds(TIMEOUT_SECONDS))\n                    .build();\n                return client.send(request, HttpResponse.BodyHandlers.ofString());\n            } catch (ConnectException e) {\n                if (retry == MAX_RETRIES - 1) {\n                    throw new DDNConnectionException(\n                        \"Failed to connect to EXAScaler at \" + endpoint,\n                        e\n                    );\n                }\n                Thread.sleep(1000 * (retry + 1));\n            }\n        }\n    }\n}"
```

#### Python

```json
"code_before": "# No validation of response\nresponse = requests.get(exascaler_url)\ndata = response.json()\nreturn data['metrics']",

"code_after": "# Add validation and error handling\nresponse = requests.get(exascaler_url, timeout=10)\nif response.status_code != 200:\n    raise DDNAPIException(\n        f\"EXAScaler API returned {response.status_code}: {response.text}\"\n    )\ntry:\n    data = response.json()\nexcept json.JSONDecodeError as e:\n    raise DDNAPIException(f\"Invalid JSON response: {e}\")\nif 'metrics' not in data:\n    raise DDNAPIException(\"Response missing 'metrics' field\")\nreturn data['metrics']"
```

#### JavaScript

```json
"code_before": "// No null check\nconst data = await fetchTenantData(tenant2Domain);\nconst files = data.files;",

"code_after": "// Verify tenant authorization before access\nif (currentTenant.domain !== requestedDomain) {\n    throw new ForbiddenError(\n        `Access denied: Tenant ${currentTenant.domain} cannot access ${requestedDomain}`\n    );\n}\nconst data = await fetchTenantData(currentTenant.domain);\nconst files = data?.files ?? [];"
```

#### Configuration Files

```json
"code_before": "# application.properties\nddn.exascaler.endpoint=http://exascaler.ddn.local:8080\n# No fallback or validation",

"code_after": "# application.properties\nddn.exascaler.endpoint=http://exascaler.ddn.local:8080\nddn.exascaler.fallback.ip=10.10.1.50\n# DNS validation on startup\nddn.dns.validation.enabled=true\nddn.dns.validation.failfast=false"
```

### Formatting Rules

1. **Use `\n` for newlines** in JSON strings
2. **Indent with 4 spaces** (use `    ` not `\t`)
3. **Keep lines under 80 characters** when possible
4. **Include context** - class declaration, method signature
5. **Comment the fix** - Add `// Added: ...` or `# Fixed: ...` comments
6. **Max length**: 2000 characters per code block (split if longer)

---

## 🗂️ Category Taxonomy

### CODE
Errors caused by code bugs, logic issues, or programming mistakes.

**Subcategories**:
- Null Pointer Access
- Array Index Out of Bounds
- Type Conversion
- Logic Errors
- Concurrency Issues

**Examples**: `NullPointerException`, `IndexOutOfBoundsException`, `ClassCastException`

---

### INFRASTRUCTURE
Errors related to external services, networks, hardware, or platform issues.

**Subcategories**:
- Network Connectivity
- Service Availability
- Resource Exhaustion
- Hardware Failure
- Storage Issues

**Examples**: `ConnectionRefusedException`, `TimeoutException`, `DiskFullException`

---

### CONFIGURATION
Errors caused by incorrect settings, missing config, or environment issues.

**Subcategories**:
- Environment Variables
- API Credentials
- DNS Configuration
- Service Endpoints
- Feature Flags

**Examples**: `AuthenticationException`, `DNSResolutionException`, `ConfigurationException`

---

### DEPENDENCY
Errors related to third-party libraries, version conflicts, or missing dependencies.

**Subcategories**:
- Version Mismatch
- Missing Library
- API Incompatibility
- Dependency Conflict

**Examples**: `ClassNotFoundException`, `NoSuchMethodException`, `VersionConflict`

---

### TEST
Errors specific to test execution, test data, or test infrastructure.

**Subcategories**:
- Test Data Issues
- Mock Configuration
- Test Environment
- Assertion Failures

**Examples**: `TestDataNotFoundException`, `MockSetupException`, `AssertionError`

---

### SECURITY
Errors related to authentication, authorization, permissions, or security policies.

**Subcategories**:
- Multi-Tenancy Isolation
- Access Control
- Credential Management
- Encryption Issues

**Examples**: `AccessDeniedException`, `CrossTenantAccessViolation`, `CredentialExpiredException`

---

## ✅ Validation Checklist

Before submitting your error documentation, verify:

### Content Quality
- [ ] **Error ID is unique** - Not already used in existing docs
- [ ] **Error message is complete** - Includes full text as seen in logs
- [ ] **Root cause is detailed** - Explains WHY, not just WHAT
- [ ] **Solution steps are actionable** - Each step can be executed
- [ ] **Code examples compile** - Before/after code is valid
- [ ] **Prevention is specific** - Includes concrete practices

### Technical Accuracy
- [ ] **Category is correct** - Follows taxonomy
- [ ] **Severity matches impact** - CRITICAL for production-blocking
- [ ] **File paths are accurate** - Point to real files in the project
- [ ] **Commands are tested** - All commands in solution_steps work
- [ ] **Related errors are valid** - Referenced error IDs exist

### Formatting
- [ ] **JSON is valid** - No syntax errors
- [ ] **Code uses `\n` for newlines** - Not literal line breaks
- [ ] **Indentation is consistent** - 4 spaces
- [ ] **Tags are lowercase-with-hyphens** - Not camelCase or PascalCase
- [ ] **Arrays don't have trailing commas** - JSON spec compliant

### Completeness
- [ ] **All required fields present** - See schema
- [ ] **At least 3 solution steps** - Detailed enough to follow
- [ ] **At least 3 tags** - Sufficient for search
- [ ] **Code_before and code_after differ** - Shows actual fix

### Writing Quality
- [ ] **No typos or grammar errors** - Proofread carefully
- [ ] **Technical terms used correctly** - No jargon misuse
- [ ] **Consistent terminology** - Same terms throughout
- [ ] **Professional tone** - Clear, concise, helpful

---

## 🚀 Loading to Pinecone

After your error documentation is merged, it must be loaded to Pinecone for RAG retrieval.

### Prerequisites

1. **Pinecone API Key** set in `.env.MASTER`:
   ```bash
   PINECONE_API_KEY=your-api-key-here
   PINECONE_ENVIRONMENT=us-east1-gcp
   ```

2. **OpenAI API Key** for embeddings:
   ```bash
   OPENAI_API_KEY=your-openai-key-here
   ```

### Loading Process

```bash
# Navigate to implementation folder
cd C:\DDN-AI-Project-Documentation\implementation

# Run the loader script
python load_error_docs_to_pinecone.py

# Expected output:
# Loading error documentation from: error-documentation.json
# Loading error documentation from: error-documentation-phase2.json
# Preparing 30 error documents...
# Creating embeddings (batch size: 10)...
# Uploading to Pinecone index: ddn-error-solutions
# ✅ Successfully loaded 30 error documents
# Pinecone stats: Total vectors: 125
```

### What the Script Does

1. **Reads JSON files** - Loads all error documentation
2. **Prepares text** - Combines fields into searchable text:
   ```python
   text = f"{error_type} {category}: {error_message} | "
   text += f"Root Cause: {root_cause} | "
   text += f"Solution: {' '.join(solution_steps)} | "
   text += f"Prevention: {prevention} | "
   text += f"Code Before: {code_before} | "
   text += f"Code After: {code_after}"
   ```
3. **Creates embeddings** - Uses OpenAI text-embedding-3-small (1536 dimensions)
4. **Uploads to Pinecone** - Stores in `ddn-error-solutions` index
5. **Stores metadata** - All fields available for filtering/display

### Verification

```bash
# Test RAG retrieval
python test_rag_query.py

# Expected: Your new error should appear in similar results
```

### Troubleshooting

**Error: Pinecone index not found**
```bash
python create_dual_pinecone_indexes.py
```

**Error: Invalid API key**
- Check `.env.MASTER` has correct keys
- Verify keys are not expired

**Error: Embedding dimension mismatch**
- Ensure using `text-embedding-3-small` (not ada-002 or other models)

---

## 📚 Examples from Existing Docs

### Example 1: ERR001 - NullPointerException (CODE Category)

```json
{
  "error_id": "ERR001",
  "error_type": "NullPointerException",
  "error_category": "CODE",
  "subcategory": "Null Pointer Access",
  "error_message": "java.lang.NullPointerException: Cannot invoke \"DDNStorage.saveDataBindFile\" because \"this.storageConfig\" is null",
  "component": "DDN Storage Configuration",
  "file_path": "src/main/java/com/ddn/storage/DDNStorage.java",
  "line_range": "125-135",
  "root_cause": "The storageConfig object is accessed without null validation. When DDN storage initialization fails or is skipped, attempting to call methods on the null storageConfig object causes NullPointerException.",
  "code_before": "public class DDNStorage {\n    private StorageConfig storageConfig;\n    \n    public void saveData(String filePath, byte[] data) {\n        // Direct access without null check\n        storageConfig.saveDataBindFile(filePath, data);\n    }\n}",
  "code_after": "public class DDNStorage {\n    private StorageConfig storageConfig;\n    \n    public void saveData(String filePath, byte[] data) {\n        // Added null check with clear error message\n        if (storageConfig == null) {\n            throw new IllegalStateException(\n                \"DDN Storage not initialized. Call init() before saveData().\"\n            );\n        }\n        storageConfig.saveDataBindFile(filePath, data);\n    }\n}",
  "solution_steps": [
    "Add null check before accessing storageConfig object",
    "Throw IllegalStateException with descriptive message",
    "Guide developer to call init() method first",
    "Prevents NPE and provides actionable error context",
    "Add @NonNull annotation to enforce initialization"
  ],
  "prevention": "Always validate object state before method calls. Use initialization flags or builder patterns.",
  "severity": "HIGH",
  "frequency": "Common in initialization flows",
  "related_errors": ["ERR002", "ERR015"],
  "test_scenarios": ["EXAScaler storage initialization", "AI400X checkpoint storage"],
  "tags": ["null-pointer", "initialization", "storage-config", "validation"]
}
```

---

### Example 2: ERR002 - ConnectionRefusedException (INFRASTRUCTURE Category)

```json
{
  "error_id": "ERR002",
  "error_type": "ConnectionRefusedException",
  "error_category": "INFRASTRUCTURE",
  "subcategory": "Network Connectivity",
  "error_message": "java.net.ConnectException: Connection refused: connect to http://exascaler.ddn.local:8080",
  "component": "EXAScaler Lustre Client",
  "file_path": "src/main/java/com/ddn/exascaler/LustreClient.java",
  "line_range": "45-52",
  "root_cause": "EXAScaler endpoint is not reachable. Common causes: service not running, incorrect hostname/port, firewall blocking connection, or DNS resolution failure.",
  "solution_steps": [
    "Verify EXAScaler service is running: systemctl status exascaler",
    "Check network connectivity: ping exascaler.ddn.local",
    "Verify DNS resolution: nslookup exascaler.ddn.local",
    "Check firewall rules allow port 8080",
    "Add retry logic with exponential backoff",
    "Configure appropriate timeouts (10-30 seconds)",
    "Provide clear error message with troubleshooting steps"
  ],
  "prevention": "Always implement retry logic for network calls. Use circuit breaker pattern for fault tolerance.",
  "severity": "CRITICAL",
  "frequency": "Common in distributed environments",
  "related_errors": ["ERR003", "ERR004", "ERR010"],
  "test_scenarios": ["EXAScaler health check", "Cluster status verification"],
  "tags": ["connection-refused", "network", "exascaler", "retry", "timeout"]
}
```

---

### Example 3: ERR011 - CrossTenantAccessViolation (SECURITY Category)

```json
{
  "error_id": "ERR011",
  "error_type": "CrossTenantAccessViolation",
  "error_category": "SECURITY",
  "subcategory": "Multi-Tenancy Isolation",
  "error_message": "HTTP 403 Forbidden: Cross-tenant access denied",
  "component": "Domain Isolation",
  "file_path": "tests/ddn-advanced-scenarios.js",
  "line_range": "145-182",
  "root_cause": "Tenant attempted to access another tenant's domain or namespace. Domain isolation is correctly preventing unauthorized cross-tenant access. This is EXPECTED behavior for security.",
  "solution_steps": [
    "Verify this is NOT a legitimate access request",
    "Confirm tenant credentials match the requested domain",
    "Check that application is using correct tenant context",
    "Review tenant routing configuration",
    "This error indicates security is WORKING - do not disable",
    "If legitimate, request admin to grant cross-tenant permissions",
    "Audit access logs for security compliance"
  ],
  "prevention": "Always validate tenant context before data access. Use middleware for automatic tenant isolation.",
  "severity": "CRITICAL",
  "frequency": "Common in multi-tenant testing",
  "related_errors": ["ERR012", "ERR013", "ERR016"],
  "test_scenarios": ["Domain isolation tests", "Cross-tenant access prevention"],
  "tags": ["security", "multi-tenancy", "403", "access-control", "domain-isolation"]
}
```

---

## 🔧 Troubleshooting

### Issue: JSON validation fails

**Error**: `Expecting ',' delimiter` or `Invalid \escape`

**Solution**:
- Check all strings are properly escaped
- Use `\n` for newlines, not actual line breaks
- No trailing commas in arrays/objects
- Validate at https://jsonlint.com/

---

### Issue: Duplicate error ID

**Error**: `error_id "ERR015" already exists`

**Solution**:
- Search all JSON files for the error ID
- Use `Ctrl+Shift+F` in VS Code
- Increment to next available ID

---

### Issue: Code examples too long

**Error**: Individual field > 2000 characters

**Solution**:
- Break into smaller, focused snippets
- Show only relevant parts (use `...` for omitted code)
- Focus on the specific problem/fix, not entire class

---

### Issue: Pinecone upload fails

**Error**: `PineconeException: Invalid vector dimensions`

**Solution**:
- Ensure using `text-embedding-3-small` (1536 dims)
- Check OPENAI_API_KEY is set correctly
- Verify model name in `load_error_docs_to_pinecone.py`

---

### Issue: Can't find error in RAG results

**Possible Causes**:
1. Not uploaded to Pinecone yet (run `load_error_docs_to_pinecone.py`)
2. Query too different from documented error
3. Embedding quality issue

**Solution**:
- Verify upload: Check Pinecone dashboard for vector count
- Test query: Run `test_rag_query.py` with your error message
- Improve documentation: Add more keywords/context to `root_cause` and `prevention`

---

## 📞 Getting Help

### Resources
- **Architecture Guide**: See `RAG-ERROR-DOCUMENTATION-GUIDE.docx` for system overview
- **RAG System**: See `ERROR-DOCUMENTATION-RAG-SYSTEM.md` for technical details
- **Phase 0B Summary**: See `PHASE-B-TASKS-SUMMARY.md` for task context

### Questions?
- **Slack**: #qa-automation channel
- **Email**: qa-team@ddn.com
- **GitHub Issues**: Label with `error-documentation`

---

## 📊 Statistics & Impact

### Current Metrics (as of 2025-11-05)
- **30+ Documented Errors**: ERR001-ERR025 and growing
- **51-72% Similarity Scores**: RAG retrieval accuracy
- **6 Error Categories**: Full taxonomy coverage
- **4 Data Sources**: Pinecone, BM25, MongoDB, PostgreSQL
- **15-20% Accuracy Boost**: From re-ranking service

### Your Contribution Makes a Difference
Every error you document:
- ✅ Helps AI provide better recommendations (15-30% accuracy improvement)
- ✅ Reduces debugging time for teammates (avg 2-3 hours saved per occurrence)
- ✅ Prevents future errors through prevention guidance
- ✅ Builds institutional knowledge

---

## 🎉 Thank You!

Your contributions to error documentation make our AI system smarter and help the entire team debug faster. Quality documentation = Better AI = Faster releases.

**Happy Documenting!** 🚀

---

**Version History**:
- **v1.0.0** (2025-11-05): Initial version with complete schema, examples, and guidelines
