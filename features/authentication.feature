Feature: Authentication guard
  As the exam API
  I want to reject requests without a valid access token
  So that exam and personal data stays protected

  Scenario: Login without an id token is rejected
    When I send a "GET" request to "/login"
    Then the response status code should be 401

  Scenario: Accessing a protected endpoint without a token is rejected
    Given I am not authenticated
    When I send a "GET" request to "/events"
    Then the response status code should be 401

  Scenario: Accessing a protected endpoint with an expired token is rejected
    Given I am authenticated with an expired token as "maria.teacher@example.test"
    When I send a "GET" request to "/events"
    Then the response status code should be 401
