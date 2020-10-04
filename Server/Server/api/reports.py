from Server.api import api
from flask_restful import Resource, reqparse, abort, marshal, fields
from Server.utils.attendance_check import Attendance
from werkzeug.datastructures import FileStorage
from Server import db, auth
from datetime import datetime
import pandas as pd
from Server.models import StudentModel, ClassroomModel, ReportModel, SessionModel, ZoomNamesModel, StudentStatus
from Server.utils.utils import create_chat_df


# marshals:
reports_list_fields = { # Fields list of classrooms
	'description': fields.String,
	'id': fields.Integer
}

student_status_field = {
    'status': fields.Integer,
    'student_name': fields.String(attribute='student.name'),
    'status_id': fields.Integer(attribute="id")
}

# args:
report_post_args = reqparse.RequestParser()
report_post_args.add_argument('description', type=str)
report_post_args.add_argument('chat_file', type=FileStorage, help="Chat file is required", location='files', required=True)
report_post_args.add_argument('time_delta', default=1, type=int)
report_post_args.add_argument('date', default=datetime.now().date(), type=lambda x: datetime.strptime(x, '%d/%m/%y'))
report_post_args.add_argument('first_sentence', type=str, help='First sentence is required in order to understand when does the check starts', required=True)
report_post_args.add_argument('not_included_zoom_users', default=[], type=str, help='Must be a list of strings with zoom names', action="append")


class ReportsResource(Resource):
    method_decorators = [auth.login_required]
    
    def get(self, class_id, report_id=None): # TODO: create decorator that validates class_id
        if ClassroomModel.query.filter_by(id=class_id, teacher=auth.current_user()).first() is None:
            abort(400, message="Invalid class id")
        if report_id is None:
            return marshal(ReportModel.query.filter_by(class_id=class_id).all(), reports_list_fields)
        report = ReportModel.query.filter_by(class_id=class_id, id=report_id).first()
        if report is None:
            abort(400, message="Invalid report id")
        return marshal(report.student_statuses, student_status_field)
        
    def post(self, class_id, report_id=None):
        args = report_post_args.parse_args()
        if ClassroomModel.query.filter_by(id=class_id, teacher=auth.current_user()).first() is None:
            abort(400, message="Invalid class id")
        if report_id:
            abort(404, message="Invalid route")

        students_df = pd.read_sql(StudentModel.query.filter_by(class_id=class_id).statement, con=db.engine)


        chat_file = args['chat_file'].stream.read().decode("utf-8").split("\n") #TODO: check this in test
        chat_df = create_chat_df(chat_file)
        report_object = Attendance(chat_df, students_df, ['name', "id_number", "phone"], args['time_delta'], args['first_sentence'], args['not_included_zoom_users'])

        message_time = report_object.first_message_time
        report_time = datetime(args["date"].year, args["date"].month, args["date"].day,
                               message_time.hour, message_time.minute, message_time.second)

        new_report = ReportModel(description=args['description'], report_time=report_time, class_id=class_id)
        db.session.add(new_report)
        db.session.commit()

        student_status_df = report_object.student_status_table(new_report.id)
        student_status_df.to_sql('student_status', con=db.engine, if_exists="append", index=False)

        for session_object in report_object.report_sessions:
            session_table = SessionModel(start_time=session_object._first_message_time, report_id=new_report.id)
            db.session.add(session_table)
            db.session.commit()

            zoom_names_df = session_object.zoom_names_table(session_table.id)
            zoom_names_df.to_sql('zoom_names', con=db.engine, if_exists="append", index=False)

            zoom_names_df = pd.read_sql(ZoomNamesModel.query.filter_by(session_id=session_table.id).statement, con=db.engine)
            session_chat_df = session_object.chat_table(zoom_names_df)
            session_chat_df.to_sql('chat', con=db.engine, if_exists="append", index=False)

        return {"report_id": new_report.id}

    def delete(self, class_id, report_id=None):
        if ClassroomModel.query.filter_by(id=class_id, teacher=auth.current_user()).first() is None:
            abort(400, message="Invalid class id")
        if report_id is None:  # Deleting all reports of class
            class_reports_id = db.session.query(ReportModel.id).filter_by(class_id=class_id).all()
            for report_data in class_reports_id:
                current_report = ReportModel.query.filter_by(id=report_data.id).first()
                db.session.delete(current_report)
            db.session.commit()
            return "", 204

        current_report = ReportModel.query.filter_by(id=report_id).first()  # Making sure the class belongs to the current user
        if current_report is None:
            abort(400, message="Invalid report id")

        db.session.delete(current_report)
        db.session.commit()
        return "", 204

api.add_resource(ReportsResource, '/classrooms/<int:class_id>/reports', '/classrooms/<int:class_id>/reports/<int:report_id>')
