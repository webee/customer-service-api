from app.utils.commons import compose
from sqlalchemy import orm, desc, asc
from sqlalchemy.sql.expression import nullslast, nullsfirst
from app.service.models import Staff

order_func_map = {
    'ascend': compose(nullsfirst, asc),
    'descend': compose(nullslast, desc),
}


def fetch_staffs(app, page, per_page, name=None, is_online=None, is_deleted=None, sorter=None, order=None):
    q = app.staffs.options(orm.undefer('context_labels'))
    if name is not None:
        pass
    if is_online is not None:
        q = q.filter(Staff.is_online == is_online)
    if is_deleted is not None:
        q = q.filter(Staff.is_deleted == is_deleted)
    order_func = order_func_map.get(order, order_func_map['descend'])
    if sorter is not None:
        if sorter == 'last_online_ts':
            q = q.order_by(order_func(Staff.last_online_ts))
        elif sorter == 'created':
            q = q.order_by(order_func(Staff.created))
        else:
            q = q.order_by(order_func(Staff.updated))
    else:
        q = q.order_by(order_func(Staff.updated))
    return q.paginate(page, per_page, error_out=False, max_per_page=100)
