*** Settings ***
Documentation     Double-Booking prevention test
Library           SeleniumLibrary
Test Setup        Open Browser To Home Page
Test Teardown     Close Browser

*** Variables ***
${BROWSER}        chrome
${SERVER_URL}     http://web:8000
${SELENIUM_URL}   http://selenium:4444/wd/hub
${LOGIN_URL}      ${SERVER_URL}/user_panel/login/
${LOGOUT_URL}     ${SERVER_URL}/user_panel/logout/
${USERNAME_1}     test_user_1
${PASSWORD_1}     password_123
${USERNAME_2}     test_user_2
${PASSWORD_2}     password_123

*** Test Cases ***
Double Booking Prevention Test
    [Documentation]    User 1 makes an appointment, User 2 tries to make the same appointment, but can't.
    Login As User    ${USERNAME_1}    ${PASSWORD_1}
    Select An Animal And Create Appointment
    Logout User
    
    Login As User    ${USERNAME_2}    ${PASSWORD_2}
    Verify Animal Term Is Unavailable For Second User
    Logout User
    
    Login As User    ${USERNAME_1}    ${PASSWORD_1}
    Cancel The Appointment

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${SERVER_URL}    ${BROWSER}    remote_url=${SELENIUM_URL}
    Maximize Browser Window

Login As User
    [Arguments]    ${username}    ${password}
    Go To    ${LOGIN_URL}
    Input Text    id=id_username    ${username}
    Input Text    id=id_password    ${password}
    Click Button  Zaloguj
    Wait Until Page Contains    Zalogowany jako:    timeout=5s

Logout User
    Go To    ${LOGOUT_URL}
    Wait Until Page Contains    Nie jesteś zalogowany    timeout=5s

Select An Animal And Create Appointment
    Go To    ${SERVER_URL}/
    Click Element    css=.product_card_link
    Wait Until Page Contains    Urodziny:
    
    Click Button    Dodaj do kalendarza
    Wait Until Page Contains    Usuń z kalendarza

Verify Animal Term Is Unavailable For Second User
    Go To    ${SERVER_URL}/
    # Klikamy w tego samego zwierzaka (pierwszego na liście)
    Click Element    css=.product_card_link
    Wait Until Page Contains    Urodziny:
    Element Should Be Disabled    xpath=//button[text()='Dodaj do kalendarza']

Cancel The Appointment
    Go To    ${SERVER_URL}/appointment/
    Wait Until Page Contains    Nadchodzące teminy spacerów 📅
    Click Button  Anuluj
    Wait Until Page Contains    No items in appointments   timeout=5s