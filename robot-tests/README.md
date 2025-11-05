# DDN Storage Robot Framework Test Suite

**Comprehensive Robot Framework tests for DDN storage products with automatic MongoDB failure reporting**

---

## 📂 Directory Structure

```
robot-tests/
├── DDN_Keywords.py              # Python keyword library
├── ddn_basic_tests.robot        # Basic product tests
├── ddn_advanced_tests.robot     # Advanced multi-tenancy tests
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd robot-tests
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
# DDN Storage Endpoints
DDN_EXASCALER_ENDPOINT=http://exascaler.ddn.local
DDN_AI400X_ENDPOINT=http://ai400x.ddn.local
DDN_INFINIA_ENDPOINT=http://infinia.ddn.local
DDN_INTELLIFLASH_ENDPOINT=http://intelliflash.ddn.local
DDN_EMF_ENDPOINT=http://emf.ddn.local
DDN_S3_ENDPOINT=http://s3.exascaler.ddn.local

# API Credentials
DDN_API_KEY=your_api_key
DDN_API_SECRET=your_api_secret
DDN_S3_ACCESS_KEY=your_s3_access_key
DDN_S3_SECRET_KEY=your_s3_secret_key

# MongoDB (for automatic failure reporting)
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/ddn_tests
MONGODB_DB=ddn_tests
```

### 3. Run Tests Locally

```bash
# Run all basic tests
robot --outputdir results ddn_basic_tests.robot

# Run all advanced tests
robot --outputdir results ddn_advanced_tests.robot

# Run specific test by tag
robot --include critical --outputdir results ddn_basic_tests.robot

# Run with MongoDB listener
robot --outputdir results --listener ../implementation/mongodb_robot_listener.py ddn_basic_tests.robot
```

---

## 📊 Test Suites Overview

### Basic Tests (`ddn_basic_tests.robot`)

**EXAScaler (Lustre) Tests:**
- ✅ Connect to Lustre file system
- ✅ Verify cluster status (MDS/OSS servers)
- ✅ Test throughput performance (TB/s)
- ✅ Create and verify Lustre striped files

**AI400X Series Tests:**
- ✅ Connect to AI storage platform
- ✅ Verify GPU-optimized performance
- ✅ Store and retrieve AI model checkpoints
- ✅ Verify 4x faster data loading claim

**Infinia Tests:**
- ✅ Connect to orchestration platform
- ✅ Optimize LLM training workloads
- ✅ Verify 15x faster checkpointing
- ✅ Setup edge-core-cloud orchestration

**IntelliFlash Tests:**
- ✅ Connect to enterprise storage
- ✅ Test CRUD operations
- ✅ Verify deduplication/compression ratios

**Integration Tests:**
- ✅ End-to-end AI pipeline verification

### Advanced Tests (`ddn_advanced_tests.robot`)

**Domain-Based Isolation:**
- ✅ Create separate domains for tenants
- ✅ Verify VLAN-based network isolation

**Multi-Tenancy:**
- ✅ Create isolated namespaces
- ✅ Configure nodemap for tenant mapping

**Quota Management:**
- ✅ Set storage quotas (soft/hard limits)
- ✅ Verify usage statistics

**S3 Multi-Tenancy:**
- ✅ Create isolated S3 buckets
- ✅ Prevent cross-tenant access

**Compliance:**
- ✅ Maintain audit logs
- ✅ Data encryption at rest
- ✅ Retention policies

---

## 🏷️ Test Tags

Use tags to run specific test categories:

| Tag | Description | Example |
|-----|-------------|---------|
| `critical` | Critical functionality tests | `robot --include critical` |
| `exascaler` | EXAScaler Lustre tests | `robot --include exascaler` |
| `ai400x` | AI400X AI storage tests | `robot --include ai400x` |
| `infinia` | Infinia optimization tests | `robot --include infinia` |
| `intelliflash` | IntelliFlash enterprise tests | `robot --include intelliflash` |
| `integration` | End-to-end integration tests | `robot --include integration` |
| `multi-tenancy` | Multi-tenancy tests | `robot --include multi-tenancy` |
| `security` | Security and isolation tests | `robot --include security` |
| `compliance` | Compliance and audit tests | `robot --include compliance` |
| `performance` | Performance benchmark tests | `robot --include performance` |

---

## 🔧 Jenkins Integration

### Jenkins Job Configuration

1. **Install Jenkins Plugins:**
   - Robot Framework Plugin
   - Git Plugin

2. **Create Jenkins Job:**
   - Use the provided `ddn-robot-tests.xml` configuration
   - Or create a new Pipeline job

3. **Jenkins Pipeline Example:**

```groovy
pipeline {
    agent any

    parameters {
        choice(name: 'TEST_SUITE', choices: ['basic', 'advanced', 'all'], description: 'Test suite to run')
        string(name: 'TEST_TAGS', defaultValue: '', description: 'Test tags (e.g., critical, exascaler)')
    }

    environment {
        MONGODB_URI = credentials('mongodb-uri')
        DDN_API_KEY = credentials('ddn-api-key')
        DDN_API_SECRET = credentials('ddn-api-secret')
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r robot-tests/requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def testFile = params.TEST_SUITE == 'all' ? '.' : "ddn_${params.TEST_SUITE}_tests.robot"
                    def tagOption = params.TEST_TAGS ? "--include ${params.TEST_TAGS}" : ''

                    sh """
                        cd robot-tests
                        robot --outputdir results \
                              --listener ../implementation/mongodb_robot_listener.py \
                              ${tagOption} \
                              ${testFile}
                    """
                }
            }
        }
    }

    post {
        always {
            robot(
                outputPath: 'robot-tests/results',
                reportFileName: 'report.html',
                logFileName: 'log.html',
                outputFileName: 'output.xml'
            )
        }
    }
}
```

---

## 📝 Writing Custom Tests

### Example Custom Test

```robot
*** Test Cases ***
Custom EXAScaler Performance Test
    [Documentation]    Custom test for specific performance requirements
    [Tags]    custom    performance
    ${response}=    Run Exascaler Throughput Benchmark
    ...    file_size_gb=50
    ...    parallel_streams=16
    Should Be Equal As Numbers    ${response.status_code}    200
    ${data}=    Set Variable    ${response.json()}
    ${throughput}=    Get From Dictionary    ${data}    throughput_gbps
    Should Be True    ${throughput} > 10.0    msg=Expected > 10 GB/s
```

### Adding New Keywords

Edit `DDN_Keywords.py`:

```python
def my_custom_keyword(self, param1, param2):
    """
    Custom keyword description

    Arguments:
    - param1: Description of param1
    - param2: Description of param2

    Returns result
    """
    url = f"{self.exascaler_endpoint}/api/v1/custom"
    data = {'param1': param1, 'param2': param2}
    response = self.session.post(url, json=data)
    return response
```

---

## 🔍 Troubleshooting

### Issue: Tests Fail with Connection Error

```
ConnectionError: Failed to establish connection
```

**Solution:**
1. Check DDN endpoint configuration in `.env`
2. Verify network connectivity: `ping exascaler.ddn.local`
3. Check firewall rules

### Issue: MongoDB Listener Not Reporting Failures

```
✗ Failed to report to MongoDB: ...
```

**Solution:**
1. Verify `MONGODB_URI` in `.env`
2. Test MongoDB connection:
   ```python
   from pymongo import MongoClient
   client = MongoClient(os.getenv('MONGODB_URI'))
   print(client.server_info())
   ```
3. Check MongoDB Atlas network access settings

### Issue: S3 Tests Fail

```
botocore.exceptions.ClientError: An error occurred (InvalidAccessKeyId)
```

**Solution:**
1. Verify S3 credentials in `.env`
2. Check S3 endpoint URL
3. Verify boto3 configuration

---

## 📈 Test Reports

Robot Framework generates three report types:

1. **report.html** - Executive summary with pass/fail statistics
2. **log.html** - Detailed test execution log with keyword-level details
3. **output.xml** - Machine-readable results for CI/CD integration

### Viewing Reports

```bash
# Open in browser
start results/report.html   # Windows
open results/report.html    # macOS
xdg-open results/report.html # Linux
```

---

## 🎯 Best Practices

1. **Use Tags Effectively:**
   - Mark critical tests with `critical` tag
   - Group related tests with product tags
   - Use `wip` tag for work-in-progress tests

2. **Implement Proper Teardown:**
   - Clean up created resources
   - Close connections
   - Delete test data

3. **Use Variables:**
   - Store configuration in variables section
   - Use suite/test variables for data sharing

4. **Write Clear Documentation:**
   - Add `[Documentation]` to all tests
   - Explain expected behavior
   - Document prerequisites

5. **Handle Errors Gracefully:**
   - Use `Run Keyword And Expect Error` for negative tests
   - Capture meaningful error messages