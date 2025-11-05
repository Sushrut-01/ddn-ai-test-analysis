*** Settings ***
Documentation    DDN Storage Basic Tests - Example Robot Framework Test
Library          RequestsLibrary
Library          Collections
Library          String
Library          OperatingSystem

*** Variables ***
${DDN_URL}              http://localhost:8080
${TIMEOUT}              30s
${EXPECTED_VERSION}     1.0.0

*** Test Cases ***
Test DDN Storage Health Check
    [Documentation]    Verify DDN storage health endpoint is responding
    [Tags]    smoke    health-check    critical
    Create Session    ddn    ${DDN_URL}    verify=False
    ${response}=    GET On Session    ddn    /api/health    timeout=${TIMEOUT}
    Should Be Equal As Numbers    ${response.status_code}    200
    Dictionary Should Contain Key    ${response.json()}    status
    Should Be Equal As Strings    ${response.json()}[status]    healthy

Test DDN Storage Version
    [Documentation]    Verify DDN storage version matches expected version
    [Tags]    smoke    version
    Create Session    ddn    ${DDN_URL}    verify=False
    ${response}=    GET On Session    ddn    /api/version
    Should Be Equal As Numbers    ${response.status_code}    200
    ${version}=    Get From Dictionary    ${response.json()}    version
    Should Be Equal    ${version}    ${EXPECTED_VERSION}

Test Domain Creation for Tenant
    [Documentation]    Test creating a new domain with tenant isolation
    [Tags]    domain    tenant    critical
    Create Session    ddn    ${DDN_URL}    verify=False
    ${domain_data}=    Create Dictionary
    ...    name=test-domain-${BUILD_NUMBER}
    ...    tenantId=tenant1
    ...    description=Test domain for tenant isolation
    ${response}=    POST On Session    ddn    /api/domains    json=${domain_data}    expected_status=201
    Should Be Equal As Numbers    ${response.status_code}    201
    Dictionary Should Contain Key    ${response.json()}    domainId
    ${domain_id}=    Get From Dictionary    ${response.json()}    domainId
    Set Suite Variable    ${DOMAIN_ID}    ${domain_id}
    Log    Created domain with ID: ${domain_id}

Test Retrieve Created Domain
    [Documentation]    Verify the created domain can be retrieved
    [Tags]    domain    retrieval
    [Setup]    Run Keyword If    '${DOMAIN_ID}' == 'NONE'    Fail    Domain not created in previous test
    Create Session    ddn    ${DDN_URL}    verify=False
    ${response}=    GET On Session    ddn    /api/domains/${DOMAIN_ID}
    Should Be Equal As Numbers    ${response.status_code}    200
    ${domain_name}=    Get From Dictionary    ${response.json()}    name
    Should Contain    ${domain_name}    test-domain

Test DNS Resolution for Domain
    [Documentation]    Test DNS resolution for domain endpoint
    [Tags]    dns    environment    critical
    ${hostname}=    Set Variable    emf.ddn.local
    ${result}=    Run Keyword And Return Status
    ...    Run    nslookup ${hostname}
    Run Keyword If    ${result} == ${False}
    ...    Fail    DNS lookup failed for ${hostname}. Please add entry to /etc/hosts or configure DNS server.

Test Storage Configuration Validation
    [Documentation]    Test storage configuration validation with null check
    [Tags]    storage    validation    negative
    Create Session    ddn    ${DDN_URL}    verify=False
    ${invalid_data}=    Create Dictionary
    ...    name=${EMPTY}
    ...    path=${NONE}
    ${response}=    POST On Session    ddn    /api/storage/config
    ...    json=${invalid_data}
    ...    expected_status=400
    Should Be Equal As Numbers    ${response.status_code}    400
    ${error}=    Get From Dictionary    ${response.json()}    error
    Should Contain    ${error}    Storage not initialized

Test Multi-Tenant Domain Isolation
    [Documentation]    Verify domains are isolated between different tenants
    [Tags]    tenant    isolation    security    critical
    Create Session    ddn    ${DDN_URL}    verify=False

    # Create domain for tenant1
    ${domain_t1}=    Create Dictionary    name=tenant1-domain    tenantId=tenant1
    ${response_t1}=    POST On Session    ddn    /api/domains    json=${domain_t1}    expected_status=201
    ${domain_id_t1}=    Get From Dictionary    ${response_t1.json()}    domainId

    # Create domain for tenant2
    ${domain_t2}=    Create Dictionary    name=tenant2-domain    tenantId=tenant2
    ${response_t2}=    POST On Session    ddn    /api/domains    json=${domain_t2}    expected_status=201
    ${domain_id_t2}=    Get From Dictionary    ${response_t2.json()}    domainId

    # Verify tenant1 cannot access tenant2's domain
    ${headers}=    Create Dictionary    X-Tenant-ID=tenant1
    ${response}=    GET On Session    ddn    /api/domains/${domain_id_t2}
    ...    headers=${headers}
    ...    expected_status=403
    Should Be Equal As Numbers    ${response.status_code}    403

Test Error Handling with NullPointerException
    [Documentation]    Reproduce and verify fix for NullPointerException in saveDataBindFile
    [Tags]    bug-fix    null-pointer    error-handling
    Create Session    ddn    ${DDN_URL}    verify=False

    # This should trigger the NPE fix from the error documentation image
    ${data}=    Create Dictionary
    ...    data=test-data
    ...    storageConfig=${NONE}

    ${response}=    POST On Session    ddn    /api/storage/databind
    ...    json=${data}
    ...    expected_status=500

    # After fix, should return 500 with clear error message
    ${error}=    Get From Dictionary    ${response.json()}    error
    Should Contain    ${error}    Storage not initialized. Call init() first.
    Log    Verified fix: Clear error message instead of NPE

Test Load Balancing Across Storage Nodes
    [Documentation]    Test load distribution across multiple storage nodes
    [Tags]    load-balancing    performance
    Create Session    ddn    ${DDN_URL}    verify=False

    # Send 10 requests and verify they're distributed
    @{node_ids}=    Create List
    FOR    ${i}    IN RANGE    10
        ${response}=    GET On Session    ddn    /api/storage/node
        ${node_id}=    Get From Dictionary    ${response.json()}    nodeId
        Append To List    ${node_ids}    ${node_id}
    END

    # Verify at least 2 different nodes were used
    ${unique_nodes}=    Remove Duplicates    ${node_ids}
    ${count}=    Get Length    ${unique_nodes}
    Should Be True    ${count} >= 2    msg=Load not distributed across multiple nodes

*** Keywords ***
Cleanup Test Data
    [Documentation]    Clean up test data after tests
    Delete All Sessions
    Remove Environment Variable    DOMAIN_ID

Create Test Domain
    [Arguments]    ${tenant_id}    ${domain_name}
    [Documentation]    Reusable keyword to create a test domain
    ${domain_data}=    Create Dictionary
    ...    name=${domain_name}
    ...    tenantId=${tenant_id}
    ${response}=    POST On Session    ddn    /api/domains    json=${domain_data}
    [Return]    ${response.json()}

Verify DNS Configuration
    [Arguments]    ${hostname}
    [Documentation]    Verify DNS configuration for given hostname
    ${result}=    Run    nslookup ${hostname}
    Should Not Contain    ${result}    server can't find
    [Return]    ${result}
