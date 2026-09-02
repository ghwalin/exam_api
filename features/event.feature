Feature: Event listing
  As a teacher
  I want to look up exam repetition events
  So that I can invite students to the right date and room

  Background:
    Given I am authenticated as the "teacher" "maria.teacher@example.test"

  Scenario: Retrieve a single event
    When I send a "GET" request to "/event/11111111-1111-1111-1111-111111111111"
    Then the response status code should be 200
    And the JSON response should have "status" equal to "open"

  Scenario: Retrieve an event that does not exist
    When I send a "GET" request to "/event/00000000-0000-0000-0000-000000000000"
    Then the response status code should be 404

  # KNOWN BUG (found while setting up this suite): EventDAO.filtered_list()
  # (data/EventDAO.py) calls event.timestamp.date() to compare against the
  # filter date, but Event.timestamp is a plain str, not a datetime - so any
  # request to GET /events/<date> currently raises AttributeError and 500s.
  # These two scenarios are tagged @known-issue and expected to fail until
  # that's fixed (e.g. by parsing timestamp with dateutil.parser first).
  @known-issue
  Scenario: List events on a given date
    When I send a "GET" request to "/events/2026-10-01"
    Then the response status code should be 200
    And the JSON response array should have 1 item

  @known-issue
  Scenario: List events on a date with nothing scheduled
    When I send a "GET" request to "/events/2099-01-01"
    Then the response status code should be 404
