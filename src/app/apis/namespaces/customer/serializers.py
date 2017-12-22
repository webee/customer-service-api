from flask_restplus import fields
from app.apis import api
from app.apis.serializers.customer import raw_customer
from app.apis.serializers.staff import raw_staff

app_customer = api.inherit('App Customer', raw_customer, {
    'user_type': fields.String(),
})

app_staff = api.inherit('App Staff', raw_staff, {
    'user_type': fields.String(),
})
