from flask_restplus import fields
from app.apis import api
from app.apis.serializers import raw_model, raw_field, raw_specs
from app.apis.serializers.project_domain_type import raw_project_domain, raw_project_domain_tree


_app_project_domain_tree_specs = {
    'name': fields.String(),
    'title': fields.String(),
    'desc': fields.String(),
    'project_domains': fields.List(fields.Nested(raw_project_domain)),
}
app_project_domain_tree = api.model('App Project Domain Tree', _app_project_domain_tree_specs)


_app_project_domain_type_tree_specs = {
    'name': fields.String(),
    'title': fields.String(),
    'desc': fields.String(),
    'project_domains': fields.List(fields.Nested(raw_project_domain_tree),
                                   attribute=lambda app: app.project_domains.all()),
}
app_project_domain_type_tree = api.model('App Project Domain Type Tree', _app_project_domain_type_tree_specs)
