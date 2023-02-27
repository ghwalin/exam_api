from dataclasses import dataclass
import datetime
import logging
from dateutil import parser
from model.Person import Person


@dataclass
class Exam(dict):
    """
    an exam to be taken
    
    author: Marcel Suter
    """

    exam_uuid: str
    event_uuid: str
    student: Person
    teacher: Person
    cohort: str
    module: str
    exam_num: str
    missed: datetime.date
    duration: int
    room: str
    remarks: str
    tools: str
    status: str

    def to_json(self, response=True) -> str:
        try:
            jstring = '{"exam_uuid":"' + self.exam_uuid + '",'
            jstring += '"cohort": "' + self.cohort + '", '
            jstring += '"module": "' + self.module + '", '
            jstring += '"exam_num": "' + self.exam_num + '", '
            jstring += '"missed": "' + self.missed.strftime("%Y-%m-%d") + '", '
            jstring += '"duration": ' + str(self.duration) + ', '
            jstring += '"room": "' + self.room + '",'
            jstring += '"remarks": "' + self.remarks + '", '
            jstring += '"tools": "' + self.tools + '", '
            jstring += '"event_uuid": "' + self.event_uuid + '", '
            jstring += '"status": "' + self.status + '", '
            if response:
                jstring += '"teacher": ' + self.teacher.to_json() + ',' + \
                           '"student": ' + self.student.to_json() + '}'
            else:
                jstring += '"teacher":"' + self.teacher.email + '",' + \
                           '"student":"' + self.student.email + '"}'
            return jstring

        except Exception:
            logging.exception("An exception was thrown!")
            logging.exception('exam_uuid: ' + self.exam_uuid)
            raise ValueError

    @property
    def exam_uuid(self) -> str:
        return self._exam_uuid

    @exam_uuid.setter
    def exam_uuid(self, value) -> None:
        self._exam_uuid = value

    @property
    def teacher(self) -> Person:
        return self._teacher

    @teacher.setter
    def teacher(self, value) -> None:
        self._teacher = value

    @property
    def student(self) -> Person:
        return self._student

    @student.setter
    def student(self, value) -> None:
        self._student = value

    @property
    def cohort(self) -> str:
        return self._cohort

    @cohort.setter
    def cohort(self, value) -> None:
        self._cohort = value

    @property
    def module(self) -> str:
        return self._module

    @module.setter
    def module(self, value) -> None:
        self._module = value

    @property
    def exam_num(self) -> str:
        return self._exam_num

    @exam_num.setter
    def exam_num(self, value) -> None:
        self._exam_num = value

    @property
    def missed(self) -> datetime:
        return self._missed

    @missed.setter
    def missed(self, value) -> None:
        if value is None or isinstance(value, datetime.date):
            self._missed = value
        else:
            self._missed = parser.parse(value)

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, value) -> None:
        self._duration = value

    @property
    def room(self) -> str:
        return self._room

    @room.setter
    def room(self, value) -> None:
        self._room = value

    @property
    def remarks(self) -> str:
        return self._remarks

    @remarks.setter
    def remarks(self, value) -> None:
        self._remarks = value

    @property
    def tools(self) -> str:
        return self._tools

    @tools.setter
    def tools(self, value) -> None:
        self._tools = value

    @property
    def event_uuid(self) -> str:
        return self._event_uuid

    @event_uuid.setter
    def event_uuid(self, value) -> None:
        self._event_uuid = value

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value) -> None:
        self._status = value


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
