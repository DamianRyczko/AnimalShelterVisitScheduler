*** Settings ***
Documentation     A single end-to-end scenario covering the main appointment flow.
Library           SeleniumLibrary
Test Setup        Open Browser To Home Page
Test Teardown     Close Browser

*** Variables ***
${BROWSER}        chrome
${SERVER_URL}     http://web:8000
${SELENIUM_URL}   http://selenium:4444/wd/hub
${LOGIN_URL}      ${SERVER_URL}/user_panel/login/
${USERNAME}       test_user
${PASSWORD}       password_123

*** Test Cases ***
Main Appointment Flow Smoke Test
    [Documentation]    Logs in, creates an appointment, cancels it, and verifies cancellation.
    Login As Test User
    Select An Animal And Create Appointment
    Cancel The Appointment
    Verify Appointment Is Cancelled

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${SERVER_URL}    ${BROWSER}    remote_url=${SELENIUM_URL}
    Maximize Browser Window

Login As Test User
    Go To    ${LOGIN_URL}
    # Fills in the forms
    Input Text    id=id_username    ${USERNAME}
    Input Text    id=id_password    ${PASSWORD}
    Click Button  Zaloguj
    Wait Until Page Contains    Zalogowany jako:    timeout=5s

Select An Animal And Create Appointment
    # Going to animal list page and selecting the first one
    Go To    ${SERVER_URL}/
    Click Element    css=.product_card_link
    Wait Until Page Contains    Urodziny:
    
    # Reservation for the first available term
    Click Button    Dodaj do kalendarza
    Wait Until Page Contains    Usuń z kalendarza

Cancel The Appointment
    # Going to appointment management site
    Go To    ${SERVER_URL}/appointment/
    Wait Until Page Contains    Nadchodzące teminy spacerów 📅
    
    # Cancels the latest appointment
    Click Button  Anuluj

Verify Appointment Is Cancelled
    Wait Until Page Contains    No items in appointments   timeout=5s
    Page Should Not Contain Element    css=.product_card_link