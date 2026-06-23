*** Settings ***
Documentation     This test checks the functionality of filters in the home page
Library           SeleniumLibrary
Test Setup        Open Browser To Home Page
Test Teardown     Close Browser

*** Variables ***
${BROWSER}             chrome
${SERVER_URL}          http://web:8000
${SELENIUM_URL}        http://selenium:4444/wd/hub
${TEST_ANIMAL_NAME}    Milka        
${TEST_CATEGORY}       Pies
${NON_EXISTING_NAME}   XYZNieistniejacy123

*** Test Cases ***
Search Animal By Title
    [Documentation]    User tries to search for the animal by its name
    Go To    ${SERVER_URL}/    
    Input Text    name=title    ${TEST_ANIMAL_NAME}
    Click Button  Zastosuj
    Wait Until Page Contains    ${TEST_ANIMAL_NAME}    timeout=5s
    Page Should Contain Element    css=.product_card_link

Filter Animals By Category
    [Documentation]    User chooses one of the categories
    Go To    ${SERVER_URL}/
    
    Select From List By Label    name=category    ${TEST_CATEGORY}
    Click Button  Zastosuj
    
    Wait Until Page Contains    ${TEST_CATEGORY}    timeout=5s
    Page Should Contain Element    css=.product_card_link

Empty Results Message
    [Documentation]    User fills in inaccurate data that dont match any animal
    Go To    ${SERVER_URL}/
    Input Text    name=title    ${NON_EXISTING_NAME}
    Click Button  Zastosuj
    Wait Until Page Contains    No cats available right now    timeout=5s
    Page Should Not Contain Element    css=.product_card_link

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${SERVER_URL}    ${BROWSER}    remote_url=${SELENIUM_URL}
    Maximize Browser Window