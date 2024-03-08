from flask_restful import Resource
from flask import make_response

from data.EventDAO import EventDAO
from util.authorization import token_required


class EventService(Resource):
    """
    services for CRUD of a single event

    author: Marcel Suter
    """

    @token_required
    def get(self, event_uuid=None):
        """
        gets an event identified by the uuid
        :param event_uuid: the unique key
        :return: http response
        """
        event_dao = EventDAO()
        http_status = 404
        jstring = ''

        event = event_dao.read_event(event_uuid)
        if event is not None:
            http_status = 200
            jstring = event.to_json()

        return make_response(
            jstring, http_status
        )
