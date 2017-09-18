from flask_restplus import fields
from . import api
from . import base_resource, raw_model


# domain
_raw_project_domain_specs = {
    'name': fields.String(required=True, min_length=1, max_length=32),
    'title': fields.String(required=True, min_length=1, max_length=32),
    'desc': fields.String(required=True, min_length=1, max_length=64),
}
project_domain = api.inherit('Project Domain', base_resource, _raw_project_domain_specs)
raw_project_domain = api.model('Pure Project Domain', _raw_project_domain_specs)


# type
_project_type_specs = {
    'domain': fields.Nested(project_domain),
    'name': fields.String(required=True, min_length=1, max_length=32),
    'title': fields.String(required=True, min_length=1, max_length=32),
    'desc': fields.String(required=True, min_length=1, max_length=64),
}
project_type = api.inherit('Project Type', base_resource, _project_type_specs)


# domain type list tree
raw_project_type = api.model('Raw Project Type', {
    'name': fields.String(),
    'title': fields.String(),
    'desc': fields.String(),
})

raw_project_domain_tree = api.inherit('Raw Project Domain Type Tree', raw_project_domain, {
    'types': fields.List(fields.Nested(raw_project_type)),
})
