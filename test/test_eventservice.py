import pytest
import util.authorization as authorization

from test.fixtures import mock_token, client, app


def test_get_single_event(monkeypatch, client):
    monkeypatch.setattr(authorization, 'token_required', mock_token)
    from service.event_service import EventService
    response = client.get('/event/32a2427d-6c14-4709-99b3-3a3e1dcd2d09')
    pass
