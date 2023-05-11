import json
from dataclasses import dataclass
from typing import List


@dataclass
class Event:
    """
    an event for exam repetitions

    author: Marcel Suter
    """

    event_uuid: str
    timestamp: str
    rooms: list
    supervisors: list
    status: str

    def to_json(self) -> str:
        jstring = '{"event_uuid":"' + self.event_uuid + '",' + \
                  '"datetime": "' + self.timestamp + '",' + \
                  '"supervisors":' + json.dumps(self.supervisors) + ',' + \
                  '"rooms":' + json.dumps(self.rooms) + ',' + \
                  '"status":' + json.dumps(self.status) + '}'
        return jstring

    @property
    def event_uuid(self) -> str:
        return self._event_uuid

    @event_uuid.setter
    def event_uuid(self, value) -> None:
        self._event_uuid = value

    @property
    def timestamp(self) -> str:
        return self._datetime

    @timestamp.setter
    def timestamp(self, value) -> None:
        self._datetime = value

    @property
    def rooms(self) -> List[str]:
        return self._rooms

    @rooms.setter
    def rooms(self, value) -> None:
        self._rooms = value

    @property
    def supervisors(self) -> List[str]:
        return self._supervisors

    @supervisors.setter
    def supervisors(self, value) -> None:
        self._supervisors = value

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value

if __name__ == '__main__':
    ''' Check if started directly '''
    pass
