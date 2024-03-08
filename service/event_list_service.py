from flask_restful import Resource
from flask import make_response

from data.EventDAO import EventDAO
from util.authorization import token_required


class EventlistService(Resource):
    """
    services for reading lists of events

    author: Marcel Suter
    """

    @token_required
    def get(self, date=None):
        """
        gets a list of events
        :param date  the date of an event
        :return: http response
        """
        event_dao = EventDAO()
        http_status = 404
        events = event_dao.filtered_list(date)
        jstring = '['
        for event in events:
            http_status = 200
            data = event.to_json() + ","
            jstring += data
        jstring = jstring[:-1] + ']'

        return make_response(
            jstring, http_status
        )
