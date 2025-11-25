# Bug #4 Fix Template - Add Suite Metadata to All reportFailure() Calls

## Pattern to Apply

For each `reportFailure()` call, add these 4 lines before the closing `});`:

```javascript
                // BUG #4 FIX: Add suite metadata for dashboard reporting
                suite_name: '<SUITE_NAME>',
                pass_count: 0,
                fail_count: 1,
                total_count: 1
```

## Suite Name Mapping by job_name

| job_name | suite_name |
|----------|------------|
| Domain-Creation-Test | Domain-Based Isolation and Management Tests |
| Domain-Isolation-Test | Domain-Based Isolation and Management Tests |
| VLAN-Isolation-Test | Domain-Based Isolation and Management Tests |
| Namespace-Creation-Test | Multi-Tenancy and Namespace Isolation Tests |
| Nodemap-Configuration-Test | Multi-Tenancy and Namespace Isolation Tests |
| Namespace-Isolation-Test | Multi-Tenancy and Namespace Isolation Tests |
| Root-Squashing-Test | Multi-Tenancy and Namespace Isolation Tests |
| Quota-Setup-Test | Quota Management and Enforcement Tests |
| Quota-Enforcement-Test | Quota Management and Enforcement Tests |
| Quota-Stats-Test | Quota Management and Enforcement Tests |
| Quota-Alert-Test | Quota Management and Enforcement Tests |
| S3-Bucket-Creation-Test | S3 Protocol Multi-Tenancy Tests |
| S3-Cross-Tenant-Access-Test | S3 Protocol Multi-Tenancy Tests |
| S3-Quota-Enforcement-Test | S3 Protocol Multi-Tenancy Tests |
| S3-Bucket-Policy-Test | S3 Protocol Multi-Tenancy Tests |
| Kerberos-Auth-Test | Kerberos Authentication and Security Tests |
| Kerberos-NID-Spoofing-Test | Kerberos Authentication and Security Tests |
| Audit-Logging-Test | Data Governance and Compliance Tests |
| Encryption-Test | Data Governance and Compliance Tests |
| Data-Retention-Test | Data Governance and Compliance Tests |

## Status

- ✅ Completed: 3/20
  - Domain-Creation-Test
  - Domain-Isolation-Test
  - VLAN-Isolation-Test

- ⏳ Remaining: 17/20
  - All others listed above

## Automated Fix Script

Use the provided Python script to complete all remaining updates:

```bash
cd tests
python fix-suite-metadata.py
```

This will add suite metadata to all 17 remaining `reportFailure()` calls.
