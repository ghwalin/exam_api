import datetime

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
            return make_response('{"message": "invalid status"}', 500)

        exam_dao = ExamDAO()
        exam = exam_dao.read_exam(exam_uuid)
        if exam is None:
            return make_response('{"message": "not found"}', 404)

        create_email(exam, status)
        http_status = 200
        return make_response('{"message": "email sent"}', http_status)

    @token_required
    @teacher_required
    def put(self, type):
        """
        sends an email to each student in a list of exams
        :param type: the type of email to send
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
                exam.invited = True
                create_email(exam, 'invitation')
        exam_dao.save_exams()
        return make_response('email sent', 200)


def create_email(exam, status):
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

    cc = [exam.teacher.email]
    if status == 'invitation':
        filename += 'invitation.txt'
        sender = chief_supervisor.email
        if chief_supervisor.email != exam.teacher.email:
            cc.append(chief_supervisor.email)
        subject = 'Aufgebot zur Nachprüfung'
    else:
        sender = exam.teacher.email
        subject = 'Verpasste Prüfung'
        if status == '10':
            if event.status == 'unassigned':
                filename += 'missed_open.txt'
            else:
                filename += 'missed.txt'
        elif status == '20' and event.status == 'unassigned':
            filename += 'missed_open.txt'
        else:
            filename += 'missed2.txt'

    file = open(filename, encoding='UTF-8')
    text = file.read()
    event_start = datetime.datetime.strptime(event.timestamp, '%Y-%m-%d %H:%M:%S')
    event_door = event_start - datetime.timedelta(minutes=15)
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
            'event.date': event_start.strftime('%d.%m.%Y'),
            'event.time': event_start.strftime('%H:%M'),
            'event.door': event_door.strftime('%H:%M'),
            'eventlist': event_dao.open_events(),
            'room': exam.room,
            'tools': exam.tools
            }
    text = replace_text(data, text)
    current_app.logger.info(f'cc={cc}')
    send_email(sender, exam.student.email, cc, subject, text)
    return True


def send_email(sender, recipient, carboncopy, subject, content):
    """
    sends an email
    :param sender: email address of the sender
    :param recipient:  email address of the recipient
    :param carboncopy: the cc recipients
    :param subject: subject of the email
    :param content: email text
    :return: None
    """
    if current_app.config['MAIL_SERVER'] == 'localhost':
        return
    mail = Mail(current_app)
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient],
        reply_to=sender,
        cc=carboncopy
    )
    msg.body = content
    mail.send(msg)
