Feature: People listing
  As a teacher
  I want to search for students and teachers by name and role
  So that I can pick the right person when creating an exam

  Background:
    Given I am authenticated as the "teacher" "maria.teacher@example.test"

  Scenario: A teacher lists matching students
    When I send a "GET" request to "/people/stefan/student"
    Then the response status code should be 200
    And the JSON response array should have 1 item

  Scenario: A teacher lists all matching people regardless of role
    When I send a "GET" request to "/people/teacher"
    Then the response status code should be 200
    And the JSON response array should have 2 items

  Scenario: A student may not list people
    Given I am authenticated as the "student" "stefan.student@example.test"
    When I send a "GET" request to "/people/maria/all"
    Then the response status code should be 401
