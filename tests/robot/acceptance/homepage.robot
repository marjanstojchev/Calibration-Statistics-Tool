*** Settings ***
Documentation     Smoke check that the React frontend loads and shows its main navigation.
...               Needs the frontend at ${FRONTEND_URL} and the API it calls.
...               Run: robot --variable FRONTEND_URL:http://localhost:5173 tests/robot/acceptance
Library           Browser
Suite Setup       New Browser    chromium    headless=True
Suite Teardown    Close Browser

*** Variables ***
${FRONTEND_URL}   http://localhost:5173

*** Test Cases ***
Homepage Shows Main Navigation
    [Tags]    smoke    acceptance
    New Page    ${FRONTEND_URL}
    Get Title    ==    cst-frontend
    Wait For Elements State    role=button[name="Protocols"]    visible    timeout=15s
    Wait For Elements State    role=button[name="Limits"]    visible
