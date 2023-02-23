from flask import make_response, current_app
from flask_mail import Mail, Message
from flask_restful import Resource, reqparse

from data.ExamDAO import ExamDAO
from data.EventDAO import EventDAO
from data.PersonDAO import PersonDAO
from util.authorization import token_required, teacher_required
from util.replace import replace_text


class EmailService(Resource):
    """
    services for sending emails
    author: Marcel Suter
    """

    def __init__(self):
        """
        constructor

        Parameters:

        """
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('exam_uuid', location='form', type=list, default=None, help='uuid', action='append')

    @token_required
    @teacher_required
    def get(self, exam_uuid, type):
        """
        sends an email
        :param exam_uuid: the unique key
        :param type: the type of email to be sent
        :return: http response
        """
        exam_dao = ExamDAO()
        exam = exam_dao.read_exam(exam_uuid)
        http_status = 404
        if exam is not None:
            self.create_email(exam, type)
            http_status = 200
        return make_response('email sent', http_status)

    @token_required
    @teacher_required
    def put(self):
        """
        sends an email to each student in a list of exams
        :return: response with path to pdf
        """
        args = self.parser.parse_args()
        exam_dao = ExamDAO()
        for exam_uuid in args['exam_uuid']:
            uuid = ''
            if isinstance(exam_uuid, list):
                for c in exam_uuid:
                    uuid += c
            else:
                uuid = exam_uuid
            exam = exam_dao.read_exam(uuid)
            if exam is not None:
                self.create_email(exam, 'invitation')
        return make_response('email sent', 200)

    def create_email(self, exam, status):
        """
        creates an email for the selected exam and type
        :param exam: the unique uuid for an exam
        :param status: the type of email (missed, ...)
        :return: successful
        """
        event_dao = EventDAO()
        event = event_dao.read_event(exam.event_uuid)
        person_dao = PersonDAO()
        chief_supervisor = person_dao.read_person(event.supervisors[0])
        filename = current_app.config['TEMPLATEPATH']

        if status == '10':
            filename += 'missed.txt'
            sender = exam.teacher.email
            subject = 'Verpasste Prüfung'
        elif status == '20':
            filename += 'missed2.txt'
            sender = exam.teacher.email
            subject = 'Verpasste Prüfung'
        else:
            filename += 'invitation.txt'
            sender = chief_supervisor.email
            subject = 'Aufgebot zur Nachprüfung'
        file = open(filename, encoding='UTF-8')
        text = file.read()
        data = {'student.firstname': exam.student.firstname,
                'student.lastname': exam.student.lastname,
                'teacher.firstname': exam.teacher.firstname,
                'teacher.lastname': exam.teacher.lastname,
                'teacher.email': exam.teacher.email,
                'chief_supervisor.firstname': chief_supervisor.firstname,
                'chief_supervisor.lastname': chief_supervisor.lastname,
                'chief_supervisor.email': chief_supervisor.email,
                'missed': exam.missed,
                'module': exam.module,
                'event.date': f'{event.timestamp[8:10]}.{event.timestamp[5:7]}.{event.timestamp[0:4]}',
                'event.time': f'{event.timestamp[14:19]}',
                'room': exam.room,
                'tools': exam.tools
                }
        text = replace_text(data, text)
        self.send_email(sender, exam.student.email, subject, text)
        return True

    def send_email(self, sender, recipient, subject, content):
        """
        sends an email
        :param sender: email address of the sender
        :param recipient:  email address of the recipient
        :param subject: subject of the email
        :param content: email text
        :return: None
        """

        mail = Mail(current_app)
        msg = Message(subject, sender=sender, recipients=[recipient], reply_to=sender)
        msg.body = content
        mail.send(msg)
        '''
        print ('From: ' + sender)
        print ('To:' + recipient)
        print (content)
        '''
