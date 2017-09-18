from flask_restplus import fields
from . import api
from . import base_resource, raw_model


# domain
_project_domain_specs = {
    'name': fields.String(required=True, min_length=1, max_length=32),
    'title': fields.String(required=True, min_length=1, max_length=32),
    'desc': fields.String(required=True, min_length=1, max_length=64),
}
project_domain = api.inherit('Project Domain', base_resource, _project_domain_specs)


# type
_project_type_specs = {
    'domain': fields.Nested(project_domain),
    'name': fields.String(required=True, min_length=1, max_length=32),
    'title': fields.String(required=True, min_length=1, max_length=32),
    'desc': fields.String(required=True, min_length=1, max_length=64),
}
project_type = api.inherit('Project Type', base_resource, _project_type_specs)


# domain type list tree
pure_project_type = api.model('Pure Project Type', {
    'name': fields.String(),
    'title': fields.String(),
    'desc': fields.String(),
})

pure_project_domain_tree = api.model('Pure Project Domain Type Tree', {
    'name': fields.String(),
    'title': fields.String(),
    'types': fields.List(fields.Nested(pure_project_type)),
})


_project_domain_type_list_tree_specs = {
    'domains': fields.List(fields.Nested(pure_project_domain_tree)),
}
