import uuid

from flask import make_response
from flask_restful import Resource, reqparse

from data.PersonDAO import PersonDAO
from util.authorization import token_required, teacher_required
from data.ExamDAO import ExamDAO
from model.Exam import Exam


class ExamService(Resource):
    """
    services for CRUD of a single exam

    author: Marcel Suter
    """

    def __init__(self):
        """
        constructor

        Parameters:

        """
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('exam_uuid', location='form', default=None, help='uuid')
        self.parser.add_argument('event_uuid', location='form', default=None, help='event_uuid')
        self.parser.add_argument('student', location='form', default=None, help='student')
        self.parser.add_argument('teacher', location='form', default=None, help='teacher')
        self.parser.add_argument('cohort', location='form', default=None, help='cohort')
        self.parser.add_argument('module', location='form', default=None, help='module')
        self.parser.add_argument('exam_num', location='form', default=None, help='exam-num')
        self.parser.add_argument('duration', location='form', type=int, default=0, help='Muss eine Ganzzahl sein')
        self.parser.add_argument('room', location='form', type=str, default='offen', help='Raum')
        self.parser.add_argument('missed', location='form', default=None, help='Muss ein gültiges Datum sein')
        self.parser.add_argument('remarks', location='form', default=None, help='remarks')
        self.parser.add_argument('tools', location='form', default=None, help='tools')
        self.parser.add_argument('status', location='form', default=None, help='status')

    @token_required
    def get(self, exam_uuid):
        """
        gets an exam identified by the uuid
        :param exam_uuid: the unique key
        :return: http response
        """
        exam_dao = ExamDAO()
        exam = exam_dao.read_exam(exam_uuid)
        data = '{}'
        http_status = 404
        if exam is not None:
            http_status = 200
            data = exam.to_json()

        return make_response(
            data, http_status
        )

    @token_required
    @teacher_required
    def post(self):
        """
        creates a new exam
        :return: http response
        """
        args = self.parser.parse_args()
        if self.save(args):
            return make_response('exam saved', 201)
        else:
            return make_response('missing parameters', 400)

    @token_required
    @teacher_required
    def put(self):
        """
        updates an existing exam identified by the uuid
        :return:
        """
        args = self.parser.parse_args()
        if self.save(args):
            return make_response('exam saved', 201)
        else:
            return make_response('missing parameters', 400)

    def save(self, args):
        """
        saves the new or updated exam
        :param args:
        :return:
        """
        exam_dao = ExamDAO()
        person_dao = PersonDAO()

        if args.exam_uuid is None or args.exam_uuid == '':
            args.exam_uuid = str(uuid.uuid4())
            exam = Exam()
        else:
            exam = exam_dao.read_exam(args.exam_uuid)

        if args.event_uuid is not None:
            exam.event_uuid = args.event_uuid
        if args.teacher is not None:
            exam.teacher = person_dao.read_person(args.teacher)
        if args.student is not None:
            exam.student = person_dao.read_person(args.student)
        if args.cohort is not None:
            exam.cohort = args.cohort
        if args.module is not None:
            exam.module = args.module
        if args.exam_num is not None:
            exam.exam_num = args.exam_num
        if args.missed is not None:
            exam.missed = args.missed
        if args.duration is not None:
            exam.duration = args.duration
        if args.room is not None:
            exam.room = args.room
        if args.remarks is not None:
            exam.remarks = args.remarks
        if args.tools is not None:
            exam.tools = args.tools
        if args.status is not None:
            exam.status = args.status

        try:
            exam_dao.save_exam(exam)
            return True
        except ValueError as e:
            return False


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
