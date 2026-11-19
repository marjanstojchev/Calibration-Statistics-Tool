*** Settings ***
Documentation     Smoke checks for the FastAPI backend. Needs the API running at ${BASE_URL}.
...               Run: robot --variable BASE_URL:http://localhost:8000 tests/robot/api
Library           RequestsLibrary
Suite Setup       Create Session    api    ${BASE_URL}
Suite Teardown    Delete All Sessions

*** Variables ***
${BASE_URL}       http://localhost:8000
${SID}            robot-smoke-session-0001
&{HEADERS}        X-Session-Id=${SID}

*** Test Cases ***
Health Endpoint Is Up
    [Tags]    smoke    api
    ${resp}=    GET On Session    api    /api/health    expected_status=anything
    Should Be Equal As Integers    ${resp.status_code}    200

Session Summary Is Returned
    [Tags]    smoke    api
    ${resp}=    GET On Session    api    /api/session    headers=${HEADERS}    expected_status=anything
    Should Be Equal As Integers    ${resp.status_code}    200

Session Request Without Id Is Rejected
    [Tags]    smoke    api
    ${resp}=    GET On Session    api    /api/session    expected_status=anything
    Should Be Equal As Integers    ${resp.status_code}    400

Limits Compute Without Protocols Is Rejected
    [Tags]    smoke    api
    &{body}=    Create Dictionary    limits_type=burn_in
    ${resp}=    POST On Session    api    /api/limits/compute    json=${body}    headers=${HEADERS}    expected_status=anything
    Should Be Equal As Integers    ${resp.status_code}    422

Delete Session Returns Deleted
    [Tags]    smoke    api
    ${resp}=    DELETE On Session    api    /api/session    headers=${HEADERS}    expected_status=anything
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    ${resp.json()}[status]    deleted
