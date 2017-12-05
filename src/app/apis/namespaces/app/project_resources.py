from flask import request
from flask_restplus import Resource, abort
from sqlalchemy.orm.exc import NoResultFound
from app import dbs
from .api import api
from app.biz import app as biz
from app.apis.jwt import current_application, require_app
from app.apis.serializers.project import project, new_project, meta_data_item
from .serializers import new_project_result


@api.route('/projects')
class ProjectCollection(Resource):
    """项目相关"""
    @require_app
    @api.expect(new_project)
    @api.marshal_with(new_project_result)
    @api.response(201, 'project is created')
    def post(self):
        """创建项目"""
        app = current_application
        data = request.get_json()
        project = biz.create_project(app, data)
        # NOTE: return project_id and xchat chat_id
        # 给后端和app端两个选择，要么后端返回chat_id, 要么app使用project_id查询cs的接口获取chat_id
        return project, 201


@api.route('/projects/<int:id>',
           '/projects/<string:domain_name>/<string:type_name>/<string:biz_id>')
class ProjectItem(Resource):
    @require_app
    @api.marshal_with(project)
    @api.response(404, 'project not found')
    def get(self, id=None, domain_name=None, type_name=None, biz_id=None):
        """获取项目"""
        app = current_application
        if id is not None:
            proj = app.projects.filter_by(id=id).one()
        elif domain_name is not None:
            pd = app.project_domains.filter_by(name=domain_name).one()
            pt = pd.types.filter_by(name=type_name).one()
            proj = pt.projects.filter_by(biz_id=biz_id).one()
        else:
            return abort(404, 'project not found')

        return proj


@api.route('/projects/<int:id>/is_exists',
           '/projects/<string:domain_name>/<string:type_name>/<string:biz_id>/is_exists')
class IsProjectItemExists(Resource):
    @require_app
    def get(self, id=None, domain_name=None, type_name=None, biz_id=None):
        """检查项目是否存在"""
        app = current_application

        is_exists = False
        if id is not None:
            is_exists = dbs.session.query(app.projects.filter_by(id=id).exists()).scalar()
        elif domain_name is not None:
            try:
                pd = app.project_domains.filter_by(name=domain_name).one()
                pt = pd.types.filter_by(name=type_name).one()
                is_exists = dbs.session.query(pt.projects.filter_by(biz_id=biz_id).exists()).scalar()
            except NoResultFound:
                pass

        return dict(is_exists=is_exists)

# TODO:
# 添加app user的信息(手机号，邮箱，性别，年龄等)


@api.route('/projects/<int:id>/data/meta')
class ProjectMetaData(Resource):
    # @require_app
    # @api.expect([meta_data_item])
    # @api.response(204, 'successfully added')
    # def post(self, id):
    #     """TODO:添加项目元数据"""
    #     app = current_application
    #     project = app.projects.filter_by(id=id).one()
    #     data = request.get_json()
    #     # TODO
    #     return None, 204
    #
    # @require_app
    # @api.expect([meta_data_item])
    # @api.response(204, 'successfully deleted')
    # def delete(self, id):
    #     """TODO:删除项目元数据"""
    #     app = current_application
    #     project = app.projects.filter_by(id=id).one()
    #     data = request.get_json()
    #     # TODO
    #     return None, 204

    @require_app
    @api.expect([meta_data_item])
    @api.response(204, 'successfully replaced')
    def put(self, id):
        """替换项目元数据"""
        app = current_application
        proj = app.projects.filter_by(id=id).one()
        data = request.get_json()
        biz.create_or_update_project_meta_data(proj, data)
        return None, 204

    # @require_app
    # @api.expect([meta_data_item])
    # @api.response(204, 'successfully updated')
    # def patch(self, id):
    #     """TODO:更新项目元数据"""
    #     app = current_application
    #     project = app.projects.filter_by(id=id).one()
    #     data = request.get_json()
    #     # TODO
    #     return None, 204


# @api.route('/projects/<int:id>/customers')
# class ProjectCustomers(Resource):
#     @require_app
#     @api.expect(raw_project_customers)
#     @api.response(204, 'successfully added')
#     def post(self, id):
#         """TODO:添加项目客户"""
#         app = current_application
#         project = app.projects.filter_by(id=id).one()
#         data = request.get_json()
#         # TODO
#         return None, 204
#
#     @require_app
#     @api.expect(raw_project_customers)
#     @api.response(204, 'successfully deleted')
#     def delete(self, id):
#         """TODO:删除项目客户"""
#         app = current_application
#         project = app.projects.filter_by(id=id).one()
#         data = request.get_json()
#         # TODO
#         return None, 204
#
#     @require_app
#     @api.expect(raw_project_customers)
#     @api.response(204, 'successfully replaced')
#     def put(self, id):
#         """TODO:替换项目客户"""
#         app = current_application
#         project = app.projects.filter_by(id=id).one()
#         data = request.get_json()
#         # TODO
#         return None, 204
#
#     @require_app
#     @api.expect(raw_project_customers)
#     @api.response(204, 'successfully updated')
#     def patch(self, id):
#         """TODO:更新项目客户"""
#         app = current_application
#         project = app.projects.filter_by(id=id).one()
#         data = request.get_json()
#         # TODO
#         return None, 204
