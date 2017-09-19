from flask_restplus import fields
from app.apis import api
from app.apis.serializers.project_domain_type import raw_project_domain, raw_project_domain_tree


_app_project_domain_tree_specs = {
    'name': fields.String(),
    'title': fields.String(),
    'desc': fields.String(),
    'project_domains': fields.List(fields.Nested(raw_project_domain), attribute='ordered_project_domains'),
}
app_project_domain_tree = api.model('App Project Domain Tree', _app_project_domain_tree_specs)


_app_project_domain_type_tree_specs = {
    'name': fields.String(),
    'title': fields.String(),
    'desc': fields.String(),
    'project_domains': fields.List(fields.Nested(raw_project_domain_tree), attribute='ordered_project_domains'),
}
app_project_domain_type_tree = api.model('App Project Domain Type Tree', _app_project_domain_type_tree_specs)
