from app.service.models import App, Customer, Staff
from app import jwt


require_app = jwt.auth_required('app')
require_customer = jwt.auth_required('customer')
require_staff = jwt.auth_required('staff')

current_app_client: App = jwt.current_identity
current_customer: Customer = jwt.current_identity
current_staff: Staff = jwt.current_identity
