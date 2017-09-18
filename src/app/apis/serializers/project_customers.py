from flask_restplus import fields
from . import api
from . import base_resource, raw_model
from .customer import customer


_project_customers_specs = {
    'parties': fields.List(fields.Nested(customer))
}
project_customers = api.inherit('Project Customers', base_resource, _project_customers_specs)
raw_project_customers = raw_model(project_customers)
