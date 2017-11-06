from flask import request
from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.service.models import Project, Session
from ..serializers.project import handling_session_item


@api.route('/projects/<string:domain_name>/<string:type_name>/my_handling_sessions')
class MyHandlingSessions(Resource):
    @require_staff
    @api.marshal_list_with(handling_session_item)
    def get(self, domain_name, type_name):
        """获取我正在接待的会话"""
        staff = current_staff
        app = staff.app

        project_domain = app.project_domains.filter_by(name=domain_name).one()
        project_type = project_domain.types.filter_by(name=type_name).one()

        sessions = staff.handling_sessions.filter(Project.type == project_type)
        res = []
        for session in sessions:
            project = session.project
            res.append(dict(
                id=session.id,
                owner=project.owner.name,
                updated=session.updated
            ))

        return res
