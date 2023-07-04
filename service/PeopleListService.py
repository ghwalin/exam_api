from flask import make_response
from flask_restful import Resource

from data.PersonDAO import PersonDAO
from util.authorization import token_required, teacher_required


class PeoplelistService(Resource):
    """
    services for reading lists of people

    author: Marcel Suter
    """
    method_decorators = [token_required]

    def __init__(self):
        """
        constructor

        Parameters:

        """
        pass

    @teacher_required
    def get(self, filter_name, filter_role='all'):
        """
        get a list of people
        :param filter_name:
        :param filter_role: the filter for the role
        :return: JSON object with the people
        """
        filter_name.replace(' ', '%20')
        person_dao = PersonDAO()
        peoplelist = person_dao.filtered_list(filter_name, filter_role)
        people_json = ' '
        for person in peoplelist:
            data = person.to_json()
            people_json += data + ','
        people_json = '[' + people_json[:-1] + ']'

        response = make_response(
            people_json,
            200
        )
        response.headers["Content-Type"] = "application/json"
        return response


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
