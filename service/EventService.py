from flask_restful import Resource, reqparse
from flask import make_response

from data.EventDAO import EventDAO
from util.authorization import token_required, teacher_required


class EventService(Resource):
    """
    services for CRUD of a single event

    author: Marcel Suter
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('status', location='form', default=None, help='status')

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

    @token_required
    @teacher_required
    def put(self, event_uuid=None):
        """
        Updates the status of the event identified by the uuid
        :param event_uuid: the unique key
        :return: http response
        """
        args = self.parser.parse_args()
        if args.status is not None:
            event_dao = EventDAO()
            if event_dao.update_event(event_uuid, args.status):
                return True
        return False
