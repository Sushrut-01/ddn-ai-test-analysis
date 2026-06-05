# PowerShell script to add suite metadata to all reportFailure() calls
# Bug #4 Fix: Ensures Jenkins build failures appear in Dashboard/MongoDB

$file = "ddn-advanced-scenarios.js"

# Suite name mappings
$suiteMappings = @{
    'Namespace-Creation-Test' = 'Multi-Tenancy and Namespace Isolation Tests'
    'Nodemap-Configuration-Test' = 'Multi-Tenancy and Namespace Isolation Tests'
    'Namespace-Isolation-Test' = 'Multi-Tenancy and Namespace Isolation Tests'
    'Root-Squashing-Test' = 'Multi-Tenancy and Namespace Isolation Tests'
    'Quota-Setup-Test' = 'Quota Management and Enforcement Tests'
    'Quota-Enforcement-Test' = 'Quota Management and Enforcement Tests'
    'Quota-Stats-Test' = 'Quota Management and Enforcement Tests'
    'Quota-Alert-Test' = 'Quota Management and Enforcement Tests'
    'S3-Bucket-Creation-Test' = 'S3 Protocol Multi-Tenancy Tests'
    'S3-Cross-Tenant-Access-Test' = 'S3 Protocol Multi-Tenancy Tests'
    'S3-Quota-Enforcement-Test' = 'S3 Protocol Multi-Tenancy Tests'
    'S3-Bucket-Policy-Test' = 'S3 Protocol Multi-Tenancy Tests'
    'Kerberos-Auth-Test' = 'Kerberos Authentication and Security Tests'
    'Kerberos-NID-Spoofing-Test' = 'Kerberos Authentication and Security Tests'
    'Audit-Logging-Test' = 'Data Governance and Compliance Tests'
    'Encryption-Test' = 'Data Governance and Compliance Tests'
    'Data-Retention-Test' = 'Data Governance and Compliance Tests'
}

# Read file content
$content = Get-Content $file -Raw

# Count existing suite_name occurrences
$beforeCount = ($content | Select-String -Pattern "suite_name:" -AllMatches).Matches.Count
Write-Host "Before: $beforeCount reportFailure() calls with suite_name"

# Apply transformations for each job_name
foreach ($jobName in $suiteMappings.Keys) {
    $suiteName = $suiteMappings[$jobName]

    # Pattern to find reportFailure calls for this job_name without suite_name
    $pattern = "(job_name: '$jobName',[^}]+?stack_trace: error\.stack)([\s\S]*?}\);\s*throw error;)"

    $replacement = "`$1,
                // BUG #4 FIX: Add suite metadata for dashboard reporting
                suite_name: '$suiteName',
                pass_count: 0,
                fail_count: 1,
                total_count: 1`$2"

    $content = $content -replace $pattern, $replacement
}

# Write back
$content | Set-Content $file -NoNewline

# Count after
$content = Get-Content $file -Raw
$afterCount = ($content | Select-String -Pattern "suite_name:" -AllMatches).Matches.Count
$added = $afterCount - $beforeCount

Write-Host "After: $afterCount reportFailure() calls with suite_name"
Write-Host ""
Write-Host "✅ Added suite metadata to $added reportFailure() calls!"
Write-Host ""
Write-Host "Status: $afterCount/20 calls now have suite metadata"
