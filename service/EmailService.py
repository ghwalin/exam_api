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
    def get(self, exam_uuid, status):
        """
        sends an email
        :param exam_uuid: the unique key
        :param status: the template for the email
        :return: http response
        """
        if status not in [None, '10', '20', '30', '35', '40']:
            return make_response('error', 500)

        exam_dao = ExamDAO()
        exam = exam_dao.read_exam(exam_uuid)
        if exam is None:
            return make_response('not found', 404)

        create_email(exam, status, False)
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
                for item in exam_uuid:
                    uuid += item
            else:
                uuid = exam_uuid
            exam = exam_dao.read_exam(uuid)
            if exam is not None:
                create_email(exam, 'invitation', True)
        return make_response('email sent', 200)


def create_email(exam, status, invitation=False):
    """
    creates an email for the selected exam and type
    :param exam: the unique uuid for an exam
    :param status: the status of the exam
    :param invitation: send invitation
    :return: successful
    """
    event_dao = EventDAO()
    event = event_dao.read_event(exam.event_uuid)
    person_dao = PersonDAO()
    chief_supervisor = person_dao.read_person(event.supervisors[0])
    filename = current_app.config['TEMPLATEPATH']

    if invitation:
        sender = [chief_supervisor.email]
        if exam.teacher.email != chief_supervisor.email:
            sender.append(exam.teacher.email)
        filename += 'invitation.txt'
        subject = f'Aufgebot zur Nachprüfung vom {event.timestamp[8:10]}.{event.timestamp[5:7]}.{event.timestamp[0:4]}'
    else:
        sender = [exam.teacher.email]
        if status == '10':
            filename += 'missed.txt'
            subject = 'Verpasste Prüfung'
        else:
            filename += 'missed2.txt'
            subject = 'Verpasste Prüfung'

    with open(filename, encoding='UTF-8') as file:
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
                'tools': exam.tools.replace('CRLF', '\n')
                }
        text = replace_text(data, text)
        send_email(sender, exam.student.email, subject, text)


def send_email(sender, recipient, subject, content):
    """
    sends an email
    :param sender: email-address of the sender
    :param recipient:  email-address of the recipient
    :param subject: subject of the email
    :param content: email text
    :return: None
    """

    mail = Mail(current_app)
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient],
        reply_to=sender[0],
        cc=sender
    )
    msg.body = content
    mail.send(msg)
