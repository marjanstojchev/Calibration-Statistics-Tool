*** Settings ***
Documentation     Session scenarios built from reusable API keywords.
Resource          ../resources/cst-api.resource
Test Tags         api    session

*** Test Cases ***
Session Summary Is Reachable
    [Tags]    smoke
    Session Summary Should Be Available    robot-smoke-session-0001