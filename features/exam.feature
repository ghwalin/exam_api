Feature: Exam management
  As a teacher
  I want to create and look up exams for students who missed the original date
  So that make-up exams can be tracked

  Background:
    Given I am authenticated as the "teacher" "maria.teacher@example.test"

  Scenario: Retrieve an existing exam
    When I send a "GET" request to "/exam/22222222-2222-2222-2222-222222222222"
    Then the response status code should be 200
    And the JSON response should have "module" equal to "M123"
    And the JSON response should have "status" equal to "20"

  Scenario: Retrieve an exam that does not exist
    When I send a "GET" request to "/exam/00000000-0000-0000-0000-000000000000"
    Then the response status code should be 404

  Scenario: A teacher creates a new exam
    When I send a "POST" request to "/exam" with form data:
      | field    | value                        |
      | student  | stefan.student@example.test |
      | teacher  | maria.teacher@example.test  |
      | cohort   | IT22a                       |
      | module   | M999                        |
      | missed   | 2026-09-20                  |
      | duration | 45                           |
      | status   | 20                           |
    Then the response status code should be 201

  Scenario: A student cannot create a new exam
    Given I am authenticated as the "student" "stefan.student@example.test"
    When I send a "POST" request to "/exam" with form data:
      | field   | value                        |
      | student | stefan.student@example.test |
      | teacher | maria.teacher@example.test  |
      | module  | M999                         |
    Then the response status code should be 401

  Scenario: Requests without a token are rejected
    Given I am not authenticated
    When I send a "GET" request to "/exam/22222222-2222-2222-2222-222222222222"
    Then the response status code should be 401
