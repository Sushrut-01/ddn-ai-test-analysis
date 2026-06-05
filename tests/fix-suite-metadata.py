#!/usr/bin/env python3
"""
Script to add suite metadata to all reportFailure() calls in test files
Bug #4 Fix: Ensures Jenkins build failures appear in Dashboard/MongoDB
"""

import re

# Suite name mappings based on describe() blocks
SUITE_MAPPINGS = {
    'Domain-Creation-Test': 'Domain-Based Isolation and Management Tests',
    'Domain-Isolation-Test': 'Domain-Based Isolation and Management Tests',
    'VLAN-Isolation-Test': 'Domain-Based Isolation and Management Tests',
    'Namespace-Creation-Test': 'Multi-Tenancy and Namespace Isolation Tests',
    'Nodemap-Configuration-Test': 'Multi-Tenancy and Namespace Isolation Tests',
    'Namespace-Isolation-Test': 'Multi-Tenancy and Namespace Isolation Tests',
    'Root-Squashing-Test': 'Multi-Tenancy and Namespace Isolation Tests',
    'Quota-Creation-Test': 'Quota Management and Enforcement Tests',
    'Quota-Enforcement-Test': 'Quota Management and Enforcement Tests',
    'Quota-Modification-Test': 'Quota Management and Enforcement Tests',
    'Quota-Deletion-Test': 'Quota Management and Enforcement Tests',
    'S3-Tenant-Isolation-Test': 'S3 Protocol Multi-Tenancy Tests',
    'S3-Bucket-Policy-Test': 'S3 Protocol Multi-Tenancy Tests',
    'S3-Cross-Tenant-Access-Test': 'S3 Protocol Multi-Tenancy Tests',
    'S3-Data-Encryption-Test': 'S3 Protocol Multi-Tenancy Tests',
    'S3-Multipart-Upload-Test': 'S3 Protocol Multi-Tenancy Tests',
    'Kerberos-Authentication-Test': 'Kerberos Authentication and Security Tests',
    'Data-Classification-Test': 'Data Governance and Compliance Tests',
    'Audit-Logging-Test': 'Data Governance and Compliance Tests',
    'Retention-Policy-Test': 'Data Governance and Compliance Tests',
}

def add_suite_metadata(file_path):
    """Add suite metadata to all reportFailure() calls"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all reportFailure calls that don't have suite_name
    pattern = r'(await reportFailure\(\{[^}]+?job_name: [\'"]([^\'\"]+)[\'"][^}]+?)(}\);)'

    def replacer(match):
        full_call = match.group(0)
        job_name = match.group(2)

        # Check if already has suite_name
        if 'suite_name:' in full_call:
            return full_call

        # Get the suite name for this job
        suite_name = SUITE_MAPPINGS.get(job_name, 'DDN Advanced Test Suite')

        # Add suite metadata before the closing brace
        metadata = f'''
                // BUG #4 FIX: Add suite metadata for dashboard reporting
                suite_name: '{suite_name}',
                pass_count: 0,
                fail_count: 1,
                total_count: 1'''

        # Insert metadata before closing brace
        return full_call.replace('});', f',{metadata}\n            }});')

    # Apply the transformation
    updated_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    # Count how many were updated
    original_count = len(re.findall(r'await reportFailure\(\{', content))
    updated_count = len(re.findall(r'suite_name:', updated_content))

    print(f"✅ Updated {file_path}")
    print(f"   Total reportFailure() calls: {original_count}")
    print(f"   Calls with suite_name: {updated_count}")

    return updated_count

if __name__ == '__main__':
    file_path = 'ddn-advanced-scenarios.js'
    count = add_suite_metadata(file_path)
    print(f"\n🎉 Successfully added suite metadata to {count} calls!")
