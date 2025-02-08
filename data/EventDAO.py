import json
from time import strptime, strftime
from typing import List

from dateutil import parser
from flask import current_app

from model.Event import Event


class EventDAO:
    """
    data access object for events

    author: Marcel Suter
    """

    def __init__(self):
        """
        constructor

        Parameters:

        """
        self._eventdict = {}
        self.load_events()

    def filtered_list(self, filter_value: str) -> List[Event]:
        """
        returns the filtered list of events
        :param filter_value: the filter to be applied
        :return: list of events
        """
        date = None
        if filter_value is not None:
            date = parser.parse(filter_value)
        filtered = []
        for (key, event) in self._eventdict.items():
            if date is None or event.timestamp.date() == date.date():
                filtered.append(event)
                if len(filtered) >= 20:
                    break
        return filtered

    def open_events(self):
        """
        returns a listing of all open events
        """
        listing = ''
        for (key, event) in self._eventdict.items():
            if event.status == 'open':
                try:
                    listing += f'  * {event.timestamp[8:10]}.{event.timestamp[5:7]}.{event.timestamp[0:4]}\n'
                except TypeError:
                    pass

        return listing

    def read_event(self, uuid: str) -> Event:

        """
        reads an event by its uuid
        :param uuid: the unique key
        :return: Exam object
        """

        if uuid in self._eventdict:
            return self._eventdict[uuid]
        return None

    def update_event(self, event_uuid, status):
        """
        Update the status of one event
        """
        if event_uuid in self._eventdict:
            event = self._eventdict[event_uuid]
            event.status = status
            self.save_events()
            return True
        return False


    def save_events(self):
        """
        Saves the events
        """

        event_json = '['
        for (key, event) in self._eventdict.items():
            event_json += event.to_json() + ','
        event_json = event_json[:-1] + ']'
        file = open(current_app.config['DATAPATH'] + 'events.json', 'w', encoding='UTF-8')
        file.write(event_json)
        file.close()

    def load_events(self) -> None:

        """
        loads all events into _eventlist
        :return: none
        :rtype: none
        """

        file = open(current_app.config['DATAPATH'] + 'events.json', encoding='UTF-8')
        events = json.load(file)
        for item in events:
            key = item['event_uuid']
            event = Event(
                item['event_uuid'],
                item['timestamp'],
                item['rooms'],
                item['supervisors'],
                item['status']
            )
            self._eventdict[key] = event


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
