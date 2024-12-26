from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restful import Api

from service.RefreshService import RefreshService
from service.EmailService import EmailService
from service.EventlistService import EventlistService
from service.AuthenticationService import AuthenticationService
from service.EventService import EventService
from service.ExamService import ExamService
from service.ExamlistService import ExamlistService
from service.PersonService import PersonService
from service.PeopleListService import PeoplelistService
from service.PrintService import PrintService

from logging.config import dictConfig

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_pyfile('./.env')
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": app.config['LOG_FILE'],
                    "formatter": "default",
                },

            },
            "root": {
                "level": app.config['LOG_LEVEL'],
                "handlers": ["console", "file"]
            },
        }
    )
    api = Api(app)

    api.add_resource(AuthenticationService, '/login')
    api.add_resource(RefreshService, '/refresh/<email>')
    api.add_resource(ExamService, '/exam', '/exam/<exam_uuid>')
    api.add_resource(ExamlistService, '/exams')
    api.add_resource(PersonService, '/person')
    api.add_resource(PeoplelistService, '/people/<filter_name>', '/people/<filter_name>/<filter_role>')
    api.add_resource(EventService, '/event', '/event/<event_uuid>')
    api.add_resource(EventlistService, '/events', '/events/<date>')
    api.add_resource(EmailService, '/email/<type>', '/email/<exam_uuid>/<status>')
    api.add_resource(PrintService, '/print', '/print/<exam_uuid>')

    @app.route('/output/<filename>')
    def send_pdf(filename):
        return send_from_directory(app.config['OUTPUTPATH'], filename)

    @app.route('/')
    @app.route('/<filename>')
    @app.route('/<folder>/<filename>')
    def send_file(folder=None, filename='index.html'):
        directory = 'static/'
        if folder is not None:
            directory += folder
        return send_from_directory(directory, filename)

    return app

app = create_app()
if __name__ == '__main__':

    app.run(debug=True)
