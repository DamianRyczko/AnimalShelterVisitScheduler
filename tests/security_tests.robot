*** Settings ***
Documentation     Negative tests confirming security and error handling
Library           SeleniumLibrary
Test Setup        Open Browser To Home Page
Test Teardown     Close Browser

*** Variables ***
${BROWSER}           chrome
${SERVER_URL}        http://web:8000
${SELENIUM_URL}      http://selenium:4444/wd/hub
${LOGIN_URL}         ${SERVER_URL}/user_panel/login/
${PROTECTED_URL}     ${SERVER_URL}/appointment/
${USERNAME}          test_user
${INVALID_PASSWORD}  ZleHaslo123!

*** Test Cases ***
Login With Invalid Credentials
    [Documentation]    User fills in incorrect password. System should turn him down
    Go To    ${LOGIN_URL}
    Input Text    id=id_username    ${USERNAME}
    Input Text    id=id_password    ${INVALID_PASSWORD}
    Click Button  Zaloguj
    
    Location Should Be    ${LOGIN_URL}
    
    Wait Until Page Contains    Please enter a correct username and password    timeout=5s

Unauthorized Access To Protected Page
    [Documentation]    Unsigned user tries to enter the appointment managment tab. System redirects them to the login section.
    Go To    ${PROTECTED_URL}
    Location Should Contain    ${LOGIN_URL}
    Page Should Contain Element    id=id_username

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${SERVER_URL}    ${BROWSER}    remote_url=${SELENIUM_URL}
    Maximize Browser Window