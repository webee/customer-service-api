from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from ..serializers import app_project_domain_tree, app_project_domain_type_tree
from app.apis.serializers.project_domain_type import raw_project_domain_tree


@api.route('/project_domains')
class AppProjectDomainCollection(Resource):
    """项目域集合"""
    @require_staff
    @api.marshal_with(app_project_domain_tree)
    def get(self):
        """获取应用项目域树"""
        staff = current_staff

        return staff.app


@api.route('/project_domains/<int:id>/types',
           '/project_domains/<string:name>/types')
class AppProjectDomainItem(Resource):
    """项目类型集合"""
    @require_staff
    @api.marshal_with(raw_project_domain_tree)
    @api.response(404, 'project domain not found.')
    def get(self, id=None, name=None):
        """获取指定项目域类型树"""
        staff = current_staff
        app = staff.app

        project_domain = None
        if id is not None:
            project_domain = app.project_domains.filter_by(id=id).one()
        elif name is not None:
            project_domain = app.project_domains.filter_by(name=name).one()

        return project_domain


@api.route('/project_domain_types')
class AppProjectDomainTypeCollection(Resource):
    """项目域和类型集合"""
    @require_staff
    @api.marshal_with(app_project_domain_type_tree)
    def get(self):
        """获取应用项目域和类型树"""
        staff = current_staff

        return staff.app
