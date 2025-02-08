from typing import List

from flask import current_app

from model.Person import Person
import json


def condition(person: Person, filter_name: str, filter_role: str) -> bool:
    """
    condition for filtering the examlist
    :param filter_role:
    :param person: a person object to be examined
    :param filter_name: the filter condition
    :return: matches filter True/False
    """
    filter_name = filter_name.lower()
    if filter_name not in person.fullname.lower():
        return False
    if filter_role != 'all' and filter_role != person.role:
        return False
    return True


class PersonDAO:
    """
    data access object for person

    author: Marcel Suter
    """

    def __init__(self):
        """
        constructor

        Parameters:

        """
        self._peopledict = {}
        self.load_people()

    def filtered_list(self, filter_name: str, filter_role: str) -> List[Person]:
        """
        returns the filtered list of people
        :param filter_name: the filter for the name
        :param filter_role: the filter for the role
        :return: list of people
        """

        filtered = []
        for (key, person) in self._peopledict.items():
            if condition(person, filter_name, filter_role):
                filtered.append(person)
        return filtered

    def read_person(self, email: str) -> Person:
        """
        reads a person by its email
        :param email:
        :return: Person object
        """
        for (key, item) in self._peopledict.items():

            if key.casefold() == email.casefold():
                return item
        return Person(
            email=email,
            firstname='***Konto gelöscht***',
            lastname='',
            department='',
            role='student'
        )

    def load_people(self) -> None:
        """
        loads all exams into _examlist
        :return: none
        :rtype: none
        """
        file = open(current_app.config['DATAPATH'] + 'people.json', encoding='UTF-8')
        people = json.load(file)
        for item in people:
            key = item['email']
            person = Person(
                item['email'],
                item['firstname'],
                item['lastname'],
                item['department'],
                item['role']
            )
            self._peopledict[key] = person


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
