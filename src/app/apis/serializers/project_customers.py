from flask_restplus import fields
from app import ma
from . import api
from . import base_resource, raw_model
from .customer import customer, RawCustomerSchema

_project_customers_specs = {
    'parties': fields.List(fields.Nested(customer))
}
project_customers = api.inherit('Project Customers', base_resource, _project_customers_specs)
raw_project_customers = raw_model(project_customers)


class RawProjectCustomersSchema(ma.Schema):
    class Meta:
        fields = ("parties",)

    parties = ma.List(ma.Nested(RawCustomerSchema))
