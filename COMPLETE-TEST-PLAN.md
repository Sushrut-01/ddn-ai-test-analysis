# DDN AI Test Failure Analysis System - Complete Test Plan

**Project:** DDN AI-Assisted Test Case Failure Analysis  
**Test Plan Version:** 1.0  
**Date:** November 25, 2025  
**Status:** Comprehensive Test Coverage Plan

---

## 🎯 Project Understanding

### System Purpose
An **AI/ML-driven autonomous system** that:
- Automatically detects and classifies test case failures from Jenkins/GitHub
- Provides intelligent root cause analysis using LangGraph + RAG + MCP
- Generates actionable code fix recommendations
- Reduces manual debugging from 60 min → 20 min per test case
- Delivers analysis via Dashboard + Microsoft Teams

### Architecture Components
1. **Data Collection Layer**: Jenkins webhooks → MongoDB Atlas
2. **Database Layer**: PostgreSQL (structured), MongoDB (unstructured), Redis (cache)
3. **AI Processing Layer**: LangGraph Agent + RAG (Pinecone) + Claude AI + MCP Tools
4. **Orchestration Layer**: n8n workflows + Celery workers
5. **Observability Layer**: Langfuse LLM monitoring + Flower task monitoring
6. **Presentation Layer**: React Dashboard + Teams notifications
7. **Testing Layer**: Robot Framework (Jenkins) + Playwright (UI E2E)

### Key Technologies
- **AI**: Claude AI, LangGraph, RAG, MCP Protocol
- **Databases**: MongoDB Atlas, PostgreSQL, Redis, Pinecone
- **Orchestration**: n8n, Celery
- **Testing**: Robot Framework, Playwright, pytest
- **Infrastructure**: Docker/Rancher Desktop, Jenkins CI/CD

---

## 📊 Test Pyramid Strategy

```
                    ┌─────────────┐
                    │   Manual    │  5%
                    │  Exploratory│
                    └─────────────┘
                ┌───────────────────┐
                │   E2E UI Tests    │  15%
                │   (Playwright)    │
                └───────────────────┘
            ┌───────────────────────────┐
            │   API Integration Tests   │  30%
            │   (pytest + requests)     │
            └───────────────────────────┘
        ┌───────────────────────────────────┐
        │   Unit Tests (pytest)             │  50%
        │   AI Logic, Services, Components  │
        └───────────────────────────────────┘
```

---

## 🧪 Test Categories

### 1. Unit Tests (50% - 200+ tests)
**Framework:** pytest  
**Location:** `implementation/tests/`

#### 1.1 AI/ML Components
- **LangGraph Agent** (`test_langgraph_*.py`)
  - ✅ RAG router logic
  - ✅ MCP tool selection
  - ✅ Error classification
  - ✅ Multi-step reasoning
  - ✅ Self-correction mechanisms

- **RAG Systems** (`test_rag_*.py`, `test_fusion_rag_*.py`, `test_crag_*.py`)
  - ✅ Dual-index architecture (Pinecone + BM25)
  - ✅ Hybrid search (vector + keyword)
  - ✅ Re-ranking service
  - ✅ Context-aware routing
  - ✅ CRAG verification

- **Prompt Engineering** (`test_prompt_templates.py`, `test_context_engineering.py`)
  - ✅ Template validation
  - ✅ Context optimization
  - ✅ Token management

#### 1.2 Core Services
- **Dashboard API** (`test_dashboard_*.py`)
  - ✅ Manual trigger endpoint
  - ✅ Failure retrieval
  - ✅ Analysis status tracking
  - ✅ User feedback loop

- **Aging Service** (`aging_service.py`)
  - ✅ Failure aging logic (7-day threshold)
  - ✅ Batch processing
  - ✅ Priority queue management

- **Integration Services**
  - ✅ GitHub client (`test_github_*.py`)
  - ✅ Jira integration (`jira_integration_service.py`)
  - ✅ Slack notifications (`slack_integration_service.py`)
  - ✅ Self-healing service

#### 1.3 Data Layer
- **Database Operations** (`test_postgres_connection.py`, `test_mongodb_*.py`)
  - ✅ PostgreSQL schema validation
  - ✅ MongoDB CRUD operations
  - ✅ Redis caching (`test_phase1_redis_caching.py`)
  - ✅ Connection pooling

- **Observability** (`test_langfuse_integration.py`, `test_flower_integration.py`)
  - ✅ Langfuse trace logging
  - ✅ Celery task monitoring
  - ✅ PII redaction

### 2. Integration Tests (30% - 120+ tests)
**Framework:** pytest + requests  
**Location:** `implementation/tests/`

#### 2.1 End-to-End AI Workflows
- **GitHub to Analysis Flow** (`test_e2e_github_integration_*.py`)
  - Test complete flow: GitHub webhook → MongoDB → LangGraph → Analysis → Dashboard
  - Verify MCP GitHub tool integration
  - Validate file content retrieval

- **Manual Trigger Flow** (`manual_trigger_api.py`)
  - API endpoint acceptance tests
  - Async job queuing
  - Status polling
  - Result delivery

#### 2.2 Service-to-Service Communication
- **n8n Orchestration**
  - Workflow execution tests
  - Webhook triggers
  - Error handling
  - Retry mechanisms

- **Celery Task Queue**
  - Task distribution
  - Worker health
  - Priority handling
  - Dead letter queue

#### 2.3 External Integrations
- **MongoDB Atlas**
  - Connection reliability
  - Query performance
  - Failure data storage
  - Index effectiveness

- **Pinecone Vector DB**
  - Vector similarity search
  - Index creation/updates
  - Query latency (<100ms target)

- **Claude AI API**
  - Rate limiting handling
  - Response validation
  - Cost tracking
  - Fallback mechanisms

### 3. UI E2E Tests (15% - 60+ tests)
**Framework:** Playwright  
**Locations:** 
- `ddn-playwright-automation/tests/ui/`
- `tests/ui/manual_analyze.spec.ts`

#### 3.1 Dashboard Core Features
**Suite:** `dashboard.spec.ts` (8 tests)
- ✅ Page load and title verification
- ✅ Service status cards display
- ✅ Manual analysis trigger
- ✅ Search failures functionality
- ✅ Filter by severity (critical/high/medium/low)
- ✅ Service status per DDN product (EXAScaler, AI400X, Infinia, IntelliFlash)
- ✅ API error handling
- ✅ Auto-refresh data validation

#### 3.2 Manual Analysis Workflow
**Suite:** `manual-analysis.spec.ts` (8 tests)
- ✅ Navigation from dashboard
- ✅ Start analysis successfully
- ✅ Progress bar tracking
- ✅ Cancel analysis in progress
- ✅ Display analysis results
- ✅ Error handling (500 responses)
- ✅ Update failures count post-analysis
- ✅ Button state management (disabled during run)

#### 3.3 Failures Page
**Suite:** `failures.spec.ts` (12 tests)
- ✅ Failures list display with data
- ✅ Failure cards with severity badges and timestamps
- ✅ Open failure details modal
- ✅ Filter by severity levels
- ✅ Correct severity badge display
- ✅ Stack trace display
- ✅ Retry failed test functionality
- ✅ Export failures data (CSV/JSON/XLSX)
- ✅ Pagination through failures
- ✅ Timestamp format validation
- ✅ Empty state handling (no failures message)
- ✅ Search failures by test name

#### 3.4 Cross-Browser Testing
**Browsers:**
- ✅ Chromium (Desktop Chrome)
- ✅ Firefox (Desktop Firefox)
- ✅ WebKit (Desktop Safari)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 13)

**CI/CD Integration:**
- GitHub Actions workflow (`playwright.yml`)
- Scheduled runs every 6 hours
- Artifact uploads (reports, screenshots, videos)

### 4. System Integration Tests (Robot Framework)
**Framework:** Robot Framework  
**Location:** `robot-tests/`  
**Jenkins Job:** DDN-Nightly-Tests

#### 4.1 DDN Basic Tests (16 tests)
**Suite:** `ddn_basic_tests.robot`

**EXAScaler (Lustre) - 4 tests**
- Connect to Lustre file system
- Verify cluster status and MDS servers
- Create and delete filesystems
- OST (Object Storage Target) verification

**AI400X Series - 4 tests**
- Health check and GPU availability
- Dataset upload and processing
- Training job submission
- Model inference validation

**Infinia - 4 tests**
- API connectivity and authentication
- Workload optimization recommendations
- Caching configuration
- Performance metrics collection

**IntelliFlash - 3 tests**
- Storage pool status
- Volume creation and snapshot management
- Replication verification

**Full Pipeline - 1 test**
- End-to-end data flow validation

#### 4.2 DDN Advanced Tests (7 tests)
**Suite:** `ddn_advanced_tests.robot`

**Multi-Tenancy - 4 tests**
- Isolated domain creation per tenant
- Namespace separation
- Bucket segregation
- Cross-tenant access prevention

**S3 Security - 2 tests**
- Access key/secret management
- Bucket policy enforcement

**Quota Management - Not implemented yet**
**Audit Logging - 1 test**
- Event capture and log verification

#### 4.3 MongoDB Listener Integration
**File:** `implementation/mongodb_robot_listener.py`
- ✅ Automatic failure capture (all 23 tests)
- ✅ MongoDB Atlas storage
- ✅ 856 total failures captured to date
- ✅ PII redaction disabled (as per client approval)
- ✅ Build metadata (job name, number, URL, Git commit)

### 5. Performance Tests (Planned)
**Framework:** Locust / pytest-benchmark  
**Status:** 🔜 To be implemented

#### 5.1 Load Testing
- Dashboard API under concurrent users (100/500/1000)
- Analysis job throughput (batches of 10/50/100)
- Database query performance under load

#### 5.2 Stress Testing
- Peak load scenarios (Black Friday-style surge)
- Memory leak detection
- Resource exhaustion recovery

#### 5.3 Performance Benchmarks
- **Analysis Speed:** <15 seconds per failure (target)
- **Dashboard Load Time:** <2 seconds
- **API Response Time:** <200ms (p95)
- **RAG Query Latency:** <100ms
- **MongoDB Query:** <50ms

### 6. Security Tests (Planned)
**Framework:** OWASP ZAP / pytest-security  
**Status:** 🔜 To be implemented

#### 6.1 Authentication & Authorization
- API key validation
- Role-based access control (RBAC)
- Token expiry handling

#### 6.2 Data Security
- PII redaction verification
- Encryption at rest (MongoDB)
- Secure API communication (HTTPS)

#### 6.3 Vulnerability Scanning
- Dependency vulnerability checks (Snyk)
- Docker image scanning
- SQL injection prevention
- XSS protection

### 7. Accessibility Tests (Planned)
**Framework:** axe-core / Lighthouse  
**Status:** 🔜 To be implemented

#### 7.1 WCAG 2.1 Compliance
- Level A compliance
- Level AA compliance (target)
- Keyboard navigation
- Screen reader compatibility

---

## 🔄 Testing Workflows

### CI/CD Pipeline (GitHub Actions)

#### Pull Request Checks
```yaml
- Unit tests (pytest)
- Integration tests (pytest)
- Playwright UI tests (chromium only)
- Code coverage report (target: 80%)
- Linting (flake8, black)
```

#### Main Branch Deployment
```yaml
- Full test suite (all frameworks)
- Multi-browser Playwright tests
- Robot Framework smoke tests
- Docker image build and push
- Deployment to staging
```

#### Scheduled Tests
```yaml
- Playwright E2E: Every 6 hours
- Robot Framework: Nightly (Jenkins)
- Performance tests: Weekly
- Security scans: Daily
```

### Jenkins CI/CD

#### DDN-Nightly-Tests Job
- **Frequency:** Nightly + Manual trigger
- **Tests:** 23 Robot Framework tests (7 advanced + 16 basic)
- **Reporting:** MongoDB Atlas + Jenkins console
- **Artifacts:** XML/HTML reports, screenshots

#### Build Pipeline
```
1. Git checkout (feature/qa-agent branch)
2. Install dependencies (pip3 + --break-system-packages)
3. Export MongoDB URI (single quotes for %40 encoding)
4. Execute Robot Framework tests with MongoDB listener
5. Capture failures to MongoDB Atlas
6. Generate reports (output.xml, log.html, report.html)
7. Archive artifacts
```

---

## 📋 Test Coverage Matrix

| Component | Unit | Integration | E2E | Robot | Total |
|-----------|------|-------------|-----|-------|-------|
| **AI/ML** | 60 | 15 | 0 | 0 | 75 |
| **Services** | 50 | 25 | 0 | 23 | 98 |
| **Dashboard** | 10 | 5 | 28 | 0 | 43 |
| **Integrations** | 30 | 20 | 0 | 0 | 50 |
| **Database** | 25 | 15 | 0 | 0 | 40 |
| **Infra** | 25 | 40 | 0 | 0 | 65 |
| **Total** | **200** | **120** | **28** | **23** | **371** |

**Overall Coverage:** ~85% (target: 80%+)

---

## 🎯 Test Scenarios by Priority

### P0 - Critical (Must Pass Before Release)
1. ✅ **Manual analysis trigger** works end-to-end
2. ✅ **Failures display** on dashboard with correct data
3. ✅ **MongoDB listener** captures all Robot Framework failures
4. ✅ **LangGraph agent** classifies errors correctly (>80% accuracy)
5. ✅ **RAG retrieval** returns relevant documents (<100ms)
6. ✅ **Dashboard API** returns failure data correctly
7. ✅ **Jenkins integration** triggers analysis automatically

### P1 - High (Should Pass for Production)
8. ✅ **User feedback loop** stores refinements correctly
9. ✅ **GitHub links** navigate to correct file:line
10. ✅ **Jenkins links** open correct build logs
11. ✅ **Service health checks** report accurately
12. ✅ **Multi-browser support** (Chromium, Firefox, WebKit)
13. ✅ **Error handling** displays user-friendly messages
14. ✅ **Langfuse traces** capture all LLM interactions

### P2 - Medium (Nice to Have)
15. ⏳ **Export failures** to CSV/JSON/XLSX
16. ⏳ **Search functionality** finds relevant failures
17. ⏳ **Filter by severity** shows correct subset
18. ⏳ **Pagination** handles large datasets (>100 failures)
19. ⏳ **Mobile responsiveness** works on Pixel 5 / iPhone 13
20. ⏳ **Auto-refresh** updates data without manual reload

### P3 - Low (Future Enhancements)
21. 🔜 **Performance tests** validate <15s analysis time
22. 🔜 **Security scans** pass OWASP ZAP checks
23. 🔜 **Accessibility** meets WCAG 2.1 Level AA
24. 🔜 **Load testing** handles 1000 concurrent users
25. 🔜 **Chaos engineering** recovers from service failures

---

## 🛠️ Testing Tools & Frameworks

### Test Execution
- **pytest** (v8.3.4) - Python unit/integration tests
- **Playwright** (v1.55.0) - UI E2E tests
- **Robot Framework** (v7.3.2) - System integration tests
- **Locust** (planned) - Performance/load tests

### Test Support
- **faker** - Test data generation
- **pytest-cov** - Code coverage reporting
- **pytest-mock** - Mocking dependencies
- **pytest-asyncio** - Async test support

### CI/CD
- **GitHub Actions** - PR checks, deployment pipeline
- **Jenkins** - Nightly Robot Framework tests
- **Docker** - Containerized test environments

### Monitoring
- **Langfuse** - LLM trace observation
- **Flower** - Celery task monitoring
- **pytest-html** - HTML test reports

---

## 📊 Test Metrics & KPIs

### Coverage Metrics
- **Code Coverage:** 85%+ (pytest-cov)
- **Branch Coverage:** 80%+ (pytest-cov)
- **UI Coverage:** 90%+ critical user paths (Playwright)
- **API Coverage:** 95%+ endpoints (pytest + requests)

### Quality Metrics
- **Test Pass Rate:** >95% (CI pipeline)
- **Flakiness Rate:** <2% (Playwright retries)
- **Mean Time to Detect (MTTD):** <5 minutes (CI)
- **Mean Time to Repair (MTTR):** <30 minutes (development)

### Performance Metrics
- **Test Execution Time (Unit):** <5 minutes
- **Test Execution Time (Integration):** <15 minutes
- **Test Execution Time (E2E):** <20 minutes
- **Test Execution Time (Robot):** <10 minutes
- **Total CI Pipeline:** <50 minutes

### Defect Metrics
- **Defect Detection Rate:** >90% in testing phase
- **Escaped Defects:** <5 per release
- **Critical Defects:** 0 in production
- **Bug Fix SLA:** <24 hours for P0, <48 hours for P1

---

## 🚀 Test Execution Plan

### Phase 1: Unit Tests (Week 1)
```bash
# Run all unit tests
cd implementation
pytest tests/ -v --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_langgraph_*.py -v
pytest tests/test_rag_*.py -v
pytest tests/test_github_*.py -v
```

### Phase 2: Integration Tests (Week 2)
```bash
# Requires services running
docker-compose -f docker-compose-unified.yml up -d

# Run integration tests
pytest tests/test_e2e_*.py -v
pytest tests/test_*_integration.py -v
```

### Phase 3: E2E UI Tests (Week 3)
```bash
# Playwright tests
cd ddn-playwright-automation
npm install
npx playwright install
npm test

# Run specific suites
npm run test:dashboard
npm run test:analysis
npm run test:failures

# Run in headed mode (see browser)
npm run test:headed
```

### Phase 4: Robot Framework Tests (Week 4)
```bash
# Requires Jenkins job setup
# Manual execution:
cd robot-tests
python3 -m robot --outputdir robot-results \
  --listener implementation.mongodb_robot_listener.MongoDBListener \
  ddn_basic_tests.robot ddn_advanced_tests.robot

# Jenkins execution:
# Trigger DDN-Nightly-Tests job at http://localhost:8081
```

### Phase 5: Regression Tests (Week 5)
```bash
# Full regression suite
pytest tests/ -v --cov=. --cov-report=html
npx playwright test
python3 -m robot robot-tests/

# Generate consolidated report
# (Custom script to merge all test results)
```

---

## 🐛 Defect Management

### Bug Lifecycle
```
New → Assigned → In Progress → Testing → Verified → Closed
```

### Severity Classification
- **P0 - Blocker**: System unusable, data loss, security breach
- **P1 - Critical**: Major feature broken, workaround exists
- **P2 - Major**: Feature partially broken, minor impact
- **P3 - Minor**: UI glitch, typo, cosmetic issue
- **P4 - Enhancement**: Future improvement, nice-to-have

### Bug Tracking
- **Tool**: GitHub Issues (ddn-ai-test-analysis repo)
- **Labels**: `bug`, `p0-blocker`, `p1-critical`, `p2-major`, `p3-minor`
- **Milestones**: Release versions (v1.0, v1.1, etc.)

---

## ✅ Test Deliverables

### Test Artifacts
1. **Test Plan** (this document)
2. **Test Cases** (Playwright specs, Robot Framework tests, pytest tests)
3. **Test Reports** (HTML, XML, JUnit)
4. **Code Coverage Reports** (pytest-cov, Codecov)
5. **Defect Reports** (GitHub Issues)
6. **Test Data** (fixtures, mock data, test databases)
7. **CI/CD Logs** (GitHub Actions, Jenkins)

### Documentation
1. **Test Strategy** (overview, approach, scope)
2. **Test Environment Setup** (QUICK-START-*.md files)
3. **Test Execution Guide** (commands, workflows)
4. **Defect Reporting Guide** (severity, priority, lifecycle)
5. **Test Automation Guide** (frameworks, patterns, best practices)

---

## 📅 Test Schedule

| Week | Phase | Activities | Deliverables |
|------|-------|------------|--------------|
| 1 | Unit Testing | Write/execute unit tests | 200+ pytest tests, 85% coverage |
| 2 | Integration Testing | Service-to-service tests | 120+ integration tests |
| 3 | E2E Testing | Playwright UI tests | 28 E2E tests, 3 suites |
| 4 | Robot Framework | Jenkins integration tests | 23 Robot tests, MongoDB integration |
| 5 | Regression | Full suite execution | Consolidated test report |
| 6 | Performance | Load/stress testing | Performance benchmarks |
| 7 | Security | Vulnerability scans | Security assessment report |
| 8 | UAT | User acceptance testing | Sign-off from stakeholders |

---

## 🎓 Test Team

### Roles & Responsibilities
- **QA Lead**: Test strategy, planning, reporting
- **Automation Engineers**: Playwright, Robot Framework, pytest
- **DevOps Engineer**: CI/CD pipeline, Docker, Jenkins
- **Performance Tester**: Load testing, benchmarks
- **Security Tester**: Vulnerability scans, penetration testing

### Skills Required
- Python, JavaScript/TypeScript
- Playwright, Robot Framework, pytest
- Docker, Jenkins, GitHub Actions
- MongoDB, PostgreSQL, Redis
- AI/ML testing concepts (LLM, RAG, MCP)

---

## 📞 Support & Resources

### Documentation
- **Project Docs**: `C:\DDN-AI-Project-Documentation\`
- **Architecture**: `architecture/COMPLETE-ARCHITECTURE.md`
- **Setup Guides**: `MONGODB-QUICKSTART.md`, `COMPLETE-SETUP-CHECKLIST.md`
- **Test Guides**: `ddn-playwright-automation/docs/`, `robot-tests/README.md`

### Tools & Access
- **GitHub Repo**: https://github.com/Sushrut-01/ddn-ai-test-analysis
- **Jenkins**: http://localhost:8081
- **Dashboard**: http://localhost:5173
- **Langfuse**: http://localhost:3001
- **Flower**: http://localhost:5555

### Contact
- **Project Owner**: Rysun Labs Pvt. Ltd.
- **Client**: DDN (Data Direct Networks)
- **QA Team**: qa-team@rysun.com
- **Support**: support@rysun.com

---

**Test Plan Approved By:**  
- QA Lead: ________________  
- Project Manager: ________________  
- Client Stakeholder: ________________

**Date:** November 25, 2025  
**Version:** 1.0  
**Status:** ✅ Ready for Execution
