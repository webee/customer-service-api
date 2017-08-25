from flask import request
from flask_restplus import Resource
from .api import api
from .serializers import raw_project, raw_project_customers, raw_project_staffs
from ..serializers import resource_id
from app.biz import app as biz
from app.utils.jwt import current_app_client, require_app


@api.route('/projects')
class ProjectCollection(Resource):
    @require_app
    @api.expect(raw_project)
    @api.marshal_with(resource_id)
    def post(self):
        """create a new project.
        """
        app = current_app_client
        data = request.get_json()
        project = biz.create_project(app.id, data)
        return project, 201


@api.route('/projects/<int:id>/customers')
class ProjectCustomers(Resource):
    @require_app
    @api.expect(raw_project_customers)
    @api.response(204, 'successfully replaced')
    def put(self, id):
        """replace project customers
        """
        app = current_app_client
        data = request.get_json()
        # TODO
        return None, 204

    @require_app
    @api.expect(raw_project_customers)
    @api.response(204, 'successfully updated')
    def patch(self, id):
        """update project customers
        """
        app = current_app_client
        data = request.get_json()
        # TODO
        return None, 204


@api.route('/projects/<int:id>/staffs')
class ProjectStaffs(Resource):
    @require_app
    @api.expect(raw_project_staffs)
    @api.response(204, 'successfully replaced')
    def put(self, id):
        """replace project staffs
        """
        app = current_app_client
        data = request.get_json()
        # TODO
        return None, 204

    @require_app
    @api.expect(raw_project_staffs)
    @api.response(204, 'successfully updated')
    def patch(self, id):
        """update project staffs
        """
        app = current_app_client
        data = request.get_json()
        # TODO
        return None, 204
