*** Settings ***
Library    RequestsLibrary
Library    Collections

*** Variables ***
${BASE_URL}    http://localhost:8000

*** Keywords ***
Create Session Headers
    [Arguments]    ${sid}=robot-smoke-session-0001
    &{headers}=    Create Dictionary    X-Session-Id=${sid}
    RETURN    ${headers}

Session Summary Should Be Available
    [Arguments]    ${sid}
    ${h}=    Create Session Headers    ${sid}
    ${r}=    GET    ${BASE_URL}/api/session    headers=${h}
    Should Be Equal As Integers    ${r.status_code}    200