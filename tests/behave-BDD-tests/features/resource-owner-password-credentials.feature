Feature: RAS OAuth2 using 'Resource Owner Password Protection Grant' flow
  (see https://digitaleq.atlassian.net/wiki/display/RASB/Sign-in+Design for flow sequence diagrams)

  This feature file tests the token return endpoints of the OAuth server API

  Background:
    Given the Django OAuth2 server is running


  Scenario: Get access token with valid credentials
    Given valid user and client credentials
    When a POST request is made to '/api/v1/tokens/'
    Then the response returns "access_token" information
    And the response returns "refresh_token" information
    And the response returns "expires_in" information
#    And the response returns UTC time to live  # TODO: Which key does this belong to in the response?
    And the response returns "scope" information
#    And the response returns state information  # TODO: Which key does this belong to in the response?
    And the response status code is 201


  Scenario Outline: Get access token with invalid credentials
    Given a <attribute> with a value of "<invalid_value>"
    When a POST request is made to '/api/v1/tokens/'
    Then information is returned saying "<error_text>"
    And the response status code is 401

    Examples: Invalid credentials
    | attribute       | invalid_value                   | error_text                        |
    | username        | invalid_username_for_bdd_test   | Unauthorized user credentials!!!  |
    | username        | ''                              | Unauthorized user credentials!!!  |
    | password        | invalid_password_for_bdd_test   | Unauthorized user credentials!!!  |
    | password        | ''                              | Unauthorized user credentials!!!  |
    | client_id       | invalid_client_id_for_bdd_test  | Invalid client credentials        |
    | client_id       | ''                              | Invalid client credentials        |
    | client_secret   | invalid_password_for_bdd_test   | Invalid client credentials        |
    | client_secret   | ''                              | Invalid client credentials        |


  # TODO: Currently, the only way to reset/unlock a user's account is via the Django OAuth2 admin UI. Could Selenium be used here?
  Scenario: Get access token after a number of unsuccessful attempts
    Given an existing user with an invalid password
    When a POST request is made to '/api/v1/tokens/' is repeated a total of 10 times
    Then information is returned saying "User account locked"
    And the response status code is 401
