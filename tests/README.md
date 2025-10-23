# DDN Storage Comprehensive Test Suite

**Complete test coverage for DDN storage products with AI-powered failure analysis**

---

## 📋 Overview

This test suite provides comprehensive testing for DDN storage solutions including:

### **Basic Product Tests** (`ddn-test-scenarios.js`)
- ✅ **EXAScaler** (Lustre file system)
- ✅ **AI400X Series** (AI storage platforms)
- ✅ **Infinia** (AI workload optimization)
- ✅ **IntelliFlash** (Enterprise storage)
- ✅ **Integration Tests** (End-to-end pipelines)
- ✅ **Performance Benchmarks**

### **Advanced Tests** (`ddn-advanced-scenarios.js`)
- ✅ **Domain-Based Isolation** (VLAN, network segmentation)
- ✅ **Multi-Tenancy** (Namespace isolation, nodemap)
- ✅ **Quota Management** (Soft/hard limits, enforcement)
- ✅ **S3 Protocol** (Multi-tenant bucket isolation)
- ✅ **Kerberos Authentication** (NID spoofing prevention)
- ✅ **Data Governance** (Audit logs, encryption, compliance)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd tests
npm install
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your actual DDN endpoints and credentials
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 3. Run Tests

```bash
# Run all tests
npm test

# Run specific test suites
npm run test:basic        # Basic product tests
npm run test:advanced     # Advanced scenarios
npm run test:exascaler    # EXAScaler only
npm run test:multitenancy # Multi-tenancy tests
npm run test:security     # Security tests
```

---

## 📁 Test Files

### `ddn-test-scenarios.js` - Basic Product Tests

**Test Categories:**

#### 1. EXAScaler (Lustre) Tests
- Lustre cluster connectivity
- Metadata server (MDS) health
- Object storage server (OSS) status
- File striping capabilities
- TB/s throughput performance

#### 2. AI400X Series Tests
- GPU Direct Storage connectivity
- AI model checkpoint storage/retrieval
- 4x faster data loading verification
- Multi-GPU concurrent access
- Low-latency validation (<100 microseconds)

#### 3. Infinia Tests
- Orchestration platform connectivity
- LLM training workload optimization
- 15x faster checkpointing verification
- Edge-core-cloud data orchestration

#### 4. IntelliFlash Tests
- Enterprise storage connectivity
- CRUD operations (Create, Read, Update, Delete)
- Deduplication and compression ratios
- Snapshot and replication features

#### 5. Integration Tests
- End-to-end AI training pipeline
- Jenkins CI/CD integration
- Real-time monitoring and alerting

#### 6. Performance Benchmarks
- Data loading speed (4x validation)
- Latency measurements (25x validation)
- Lustre parallel I/O scalability

**Example Run:**
```bash
npm run test:basic

# Output:
# ✓ should connect to EXAScaler Lustre file system (145ms)
# ✓ should verify cluster status and metadata servers (230ms)
# ✓ should test Lustre throughput performance (1250ms)
# ...
# Total: 20 tests passed
```

---

### `ddn-advanced-scenarios.js` - Advanced Multi-Tenancy Tests

**Test Categories:**

#### 1. Domain-Based Isolation (3 tests)
- **Domain Creation**: Separate domains for Tenant 1 and Tenant 2
- **Cross-Domain Access Prevention**: Verify Tenant 1 cannot access Tenant 2's data
- **VLAN Isolation**: Verify network-level separation (VLAN 100 vs VLAN 200)

**Example:**
```javascript
// Test verifies this FAILS (good security)
await axios.get('/tenant2/data', {
    headers: {'X-Tenant': 'tenant1'}
});
// Expected: 403 Forbidden
```

#### 2. Multi-Tenancy & Namespace Isolation (4 tests)
- **Subdirectory Mount**: Create isolated namespaces `/lustre/tenant1`, `/lustre/tenant2`
- **Nodemap Configuration**: Map client NIDs to specific namespaces
- **Cross-Tenant Access Prevention**: Ensure Tenant 1 cannot list Tenant 2's files
- **Root Squashing**: Verify root user mapped to UID 1001 (not 0)

**Key Concepts:**
- **Fileset**: Subdirectory mount that restricts tenant view
- **Nodemap**: Maps client Network ID (NID) to namespace
- **Root Squashing**: Prevents privilege escalation in VMs/containers

#### 3. Quota Management (4 tests)
- **Quota Setup**: Soft limit (900GB), Hard limit (1000GB) for Tenant 1
- **Hard Limit Enforcement**: Writing 600GB to 500GB quota should FAIL
- **Usage Statistics**: Verify accurate quota reporting
- **Soft Limit Alerts**: Warning when >90% quota used

**Example:**
```javascript
// Tenant 2 has 500GB quota, tries to write 600GB
await writeFile(600GB);
// Expected: 507 Insufficient Storage Error
```

#### 4. S3 Protocol Multi-Tenancy (4 tests)
- **S3 Bucket Creation**: Isolated buckets per tenant
- **Cross-Tenant S3 Access Prevention**: Tenant 1 cannot list Tenant 2's S3 bucket
- **S3 Quota Enforcement**: 600GB upload to 500GB quota fails
- **S3 Bucket Policies**: Tenant-specific IAM policies

#### 5. Kerberos Authentication (2 tests)
- **Kerberos Login**: Authenticate via Kerberos ticket
- **NID Spoofing Prevention**: Valid NID + wrong Kerberos principal = FAIL

**Security Levels:**
- **Method A**: Basic nodemap (no root access on clients)
- **Method B**: Kerberos (prevents NID spoofing)  ✓ **Recommended**
- **Method C**: Lustre routers (network-level enforcement)

#### 6. Data Governance & Compliance (3 tests)
- **Audit Logging**: All operations logged with timestamp, user, action
- **Encryption at Rest**: AES-256-GCM encryption verified
- **Data Retention**: WORM (Write Once Read Many) compliance mode

**Example Run:**
```bash
npm run test:advanced

# Output:
# Domain-Based Isolation Tests
#   ✓ should create separate domains for tenants (320ms)
#   ✓ should enforce domain isolation (180ms)
#   ✓ should verify VLAN-based network isolation (210ms)
#
# Multi-Tenancy Tests
#   ✓ should create isolated namespaces (245ms)
#   ✓ should configure nodemap (190ms)
#   ✓ should prevent cross-tenant access (120ms)
#   ✓ should verify root squashing (95ms)
# ...
# Total: 20 tests passed
```

---

## 🔧 Configuration Guide

### Required Endpoints

Configure these in `.env`:

```env
# Core DDN Products
DDN_EXASCALER_ENDPOINT=http://exascaler.ddn.local:8080
DDN_AI400X_ENDPOINT=http://ai400x.ddn.local:8080
DDN_INFINIA_ENDPOINT=http://infinia.ddn.local:8080
DDN_INTELLIFLASH_ENDPOINT=http://intelliflash.ddn.local:8080

# Management API
DDN_EMF_ENDPOINT=http://emf.ddn.local:9090

# Multi-Protocol
DDN_S3_ENDPOINT=http://s3.exascaler.ddn.local:9000
DDN_NFS_ENDPOINT=nfs://nfs.exascaler.ddn.local:/exports
```

### Multi-Tenancy Configuration

```env
# Tenant 1
TENANT1_DOMAIN=tenant1.ddn.local
TENANT1_USER=tenant1_admin
TENANT1_VLAN=100
TENANT1_QUOTA_GB=1000

# Tenant 2
TENANT2_DOMAIN=tenant2.ddn.local
TENANT2_USER=tenant2_admin
TENANT2_VLAN=200
TENANT2_QUOTA_GB=500
```

### Authentication

```env
# DDN API
DDN_API_KEY=your-api-key
DDN_API_SECRET=your-api-secret

# S3 Credentials
DDN_S3_ACCESS_KEY=your-s3-key
DDN_S3_SECRET_KEY=your-s3-secret

# Kerberos
KERBEROS_REALM=DDN.LOCAL
KERBEROS_KDC=kdc.ddn.local:88
```

---

## 📊 Test Commands Reference

### Run by Product

```bash
npm run test:exascaler      # EXAScaler (Lustre) tests only
npm run test:ai400x         # AI400X tests only
npm run test:infinia        # Infinia tests only
npm run test:intelliflash   # IntelliFlash tests only
```

### Run by Category

```bash
npm run test:domain         # Domain isolation tests
npm run test:multitenancy   # Multi-tenancy tests
npm run test:quota          # Quota management tests
npm run test:s3             # S3 protocol tests
npm run test:kerberos       # Kerberos authentication tests
npm run test:compliance     # Compliance & governance tests
```

### Run by Type

```bash
npm run test:security       # All security-related tests
npm run test:integration    # Integration tests
npm run test:performance    # Performance benchmarks
```

### Jenkins Integration

```bash
npm run test:jenkins        # Output JUnit XML for Jenkins
```

### Development

```bash
npm run test:watch          # Watch mode for development
```

---

## 🔄 Jenkins Integration

### Jenkinsfile Configuration

Add to your `Jenkinsfile`:

```groovy
pipeline {
    agent any

    stages {
        stage('Run DDN Tests') {
            steps {
                dir('tests') {
                    sh 'npm install'
                    sh 'npm run test:jenkins'
                }
            }
        }

        stage('Report Failures') {
            when {
                expression { currentBuild.result == 'FAILURE' }
            }
            steps {
                script {
                    // Failures automatically sent to n8n webhook
                    // AI analysis triggered
                    // Results appear in dashboard
                }
            }
        }
    }

    post {
        always {
            junit 'tests/test-results/*.xml'
        }
    }
}
```

### Automatic Failure Reporting

When tests fail:

1. ✅ **Test fails** → `reportFailure()` called
2. ✅ **Data sent to n8n** → `http://localhost:5678/webhook/ddn-test-failure`
3. ✅ **Stored in MongoDB** → Status: `PENDING_ANALYSIS`
4. ✅ **Appears in dashboard** → User sees failure
5. ✅ **User clicks "Analyze Now"** → AI analysis triggered
6. ✅ **Results displayed** → Root cause + GitHub links

---

## 🧪 Writing New Tests

### Test Structure

```javascript
describe('Your Test Category', function() {
    this.timeout(config.testTimeout);

    it('should do something specific', async function() {
        try {
            // Your test code
            const response = await axios.get(endpoint);
            expect(response.status).to.equal(200);

        } catch (error) {
            // Report failure to AI system
            await reportFailure({
                build_id: `BUILD_${Date.now()}`,
                job_name: 'Your-Test-Name',
                test_name: 'should do something specific',
                test_category: 'YOUR_CATEGORY',
                product: 'EXAScaler',
                status: 'FAILURE',
                error_message: error.message,
                stack_trace: error.stack
            });
            throw error;
        }
    });
});
```

### Test Categories

Use these `test_category` values for proper AI classification:

- `STORAGE_CONNECTIVITY` - Connection tests
- `CLUSTER_HEALTH` - Cluster status tests
- `PERFORMANCE` - Performance benchmarks
- `FILE_OPERATIONS` - File CRUD operations
- `AI_STORAGE` - AI-specific storage tests
- `DOMAIN_MANAGEMENT` - Domain isolation tests
- `MULTI_TENANCY` - Multi-tenancy tests
- `QUOTA_MANAGEMENT` - Quota tests
- `SECURITY` - Security tests
- `AUTHENTICATION` - Auth tests
- `COMPLIANCE` - Compliance tests
- `INTEGRATION` - End-to-end tests

---

## 📈 Expected Test Results

### Pass Criteria

#### EXAScaler Tests
- ✅ Cluster connectivity: 200 OK
- ✅ MDS servers: >0 metadata servers online
- ✅ Throughput: >1 GB/s

#### AI400X Tests
- ✅ GPU Direct Storage: Enabled
- ✅ Latency: <100 microseconds
- ✅ Data loading speedup: >3.5x

#### Infinia Tests
- ✅ Service status: 'Infinia' response
- ✅ Checkpointing speedup: >12x

#### Multi-Tenancy Tests
- ✅ Cross-domain access: 403/401 Forbidden (expected failure)
- ✅ Root squashing: UID = 1001 (not 0)
- ✅ Quota exceeded: 507 Insufficient Storage (expected failure)
- ✅ S3 cross-tenant: AccessDenied (expected failure)

---

## 🔍 Troubleshooting

### Tests Failing to Connect

```bash
# Check endpoint accessibility
curl http://exascaler.ddn.local:8080/api/v1/health

# Verify DNS resolution
nslookup exascaler.ddn.local

# Check network connectivity
ping exascaler.ddn.local
```

### Authentication Errors

```bash
# Verify API key
echo $DDN_API_KEY

# Test authentication manually
curl -H "Authorization: Bearer $DDN_API_KEY" \
     http://exascaler.ddn.local:8080/api/v1/health
```

### Quota Tests Always Passing

This means quota enforcement is NOT working (security issue):

```javascript
// Expected: This should FAIL with 507 error
await writeFile(600GB_to_500GB_quota);

// If it succeeds, quota enforcement is broken!
```

**Fix**: Check quota configuration in DDN EMF

### Multi-Tenancy Isolation Not Working

If cross-tenant access succeeds (returns 200 OK), **this is a critical security issue**:

```javascript
// Tenant 1 accessing Tenant 2's data
// Expected: 403 Forbidden
// Actual: 200 OK ← SECURITY BREACH!
```

**Fix**: Verify nodemap configuration and VLAN isolation

---

## 📚 Understanding Multi-Tenancy Concepts

### Fileset (Subdirectory Mount)

**What it is:**
- Instead of mounting `/lustre` (root), mount `/lustre/tenant1`
- Tenant only sees their subdirectory

**Why it matters:**
- Prevents tenants from browsing other tenants' directories
- Foundation of namespace isolation

### Nodemap

**What it is:**
- Maps client Network IDs (NIDs) to specific filesets
- Example: `10.100.0.0/24@tcp` → `/lustre/tenant1`

**Why it matters:**
- Enforces which clients can access which namespaces
- Works at network level

### Root Squashing

**What it is:**
- Maps root user (UID 0) to regular user (UID 1001)

**Why it matters:**
- In VMs/containers, users often have root
- Without squashing, they could access all files
- With squashing, root becomes regular user with normal permissions

### VLAN Isolation

**What it is:**
- Each tenant on separate VLAN (100, 200, 300)
- Network-level separation

**Why it matters:**
- Even if nodemap misconfigured, VLANs prevent cross-tenant traffic
- Defense in depth

---

## 🎯 Real-World Scenarios

### Scenario 1: Healthcare Multi-Tenancy

**Requirements:**
- Hospital A and Hospital B share storage
- HIPAA compliance required
- No cross-hospital data access

**Tests:**
```bash
npm run test:multitenancy
npm run test:compliance
npm run test:security
```

**Must Pass:**
- Cross-tenant access returns 403
- Audit logs enabled
- Encryption enabled (AES-256-GCM)

### Scenario 2: AI Training with Quotas

**Requirements:**
- Team A: 1TB quota
- Team B: 500GB quota
- 4x faster data loading

**Tests:**
```bash
npm run test:quota
npm run test:ai400x
npm run test:performance
```

**Must Pass:**
- Quota enforcement (507 error when exceeded)
- Data loading >3.5x faster
- Multi-GPU access working

### Scenario 3: S3 Multi-Tenant Object Storage

**Requirements:**
- Each tenant gets S3 bucket
- No cross-bucket access
- Bucket quotas enforced

**Tests:**
```bash
npm run test:s3
```

**Must Pass:**
- Bucket creation successful
- Cross-tenant S3 access denied
- S3 quota enforced

---

## 📞 Support & Resources

### DDN Documentation
- **EXAScaler**: https://www.ddn.com/products/lustre-file-system-exascaler/
- **Multi-Tenancy**: https://www.ddn.com/blog/leveraging-isolation-lustre-file-systems/
- **EMF API**: Contact DDN support for API documentation

### Getting Help

**Test failures being reported to AI?**
Check n8n webhook: `http://localhost:5678/webhook/ddn-test-failure`

**Dashboard not showing failures?**
Verify MongoDB connection and dashboard API

**Need API documentation?**
Contact DDN support or your DDN account team

---

## ✅ Checklist Before Running Tests

- [ ] DDN storage systems accessible
- [ ] `.env` file configured with endpoints
- [ ] API keys and credentials set
- [ ] MongoDB running (for failure storage)
- [ ] n8n running (for AI analysis)
- [ ] Dashboard running (optional, for UI)
- [ ] Network connectivity to DDN endpoints verified
- [ ] Multi-tenancy features enabled in DDN (if testing advanced scenarios)

---

## 📊 Test Coverage Summary

| Category | Basic Tests | Advanced Tests | Total |
|----------|-------------|----------------|-------|
| **EXAScaler** | 4 | 7 | 11 |
| **AI400X** | 5 | - | 5 |
| **Infinia** | 4 | - | 4 |
| **IntelliFlash** | 4 | - | 4 |
| **Multi-Tenancy** | - | 8 | 8 |
| **S3 Protocol** | - | 4 | 4 |
| **Security** | - | 5 | 5 |
| **Integration** | 3 | - | 3 |
| **Performance** | 3 | - | 3 |
| **TOTAL** | **23** | **24** | **47** |

---

**Status:** Production Ready ✅
**Version:** 2.0.0
**Last Updated:** October 23, 2025
**Maintained by:** Rysun Labs Development Team

**Get started:** `npm install && npm test` 🚀
