from app.utils.commons import compose
from sqlalchemy import orm, desc, asc, func
from sqlalchemy.sql.expression import nullslast, nullsfirst
from app.service.models import Staff
from app.service import path_labels

order_func_map = {
    'ascend': compose(nullsfirst, asc),
    'descend': compose(nullslast, desc),
}


def staff_fetch_staffs(app, staff, page, per_page, uid=None, context_label=None, is_online=None,
                       is_deleted=None,
                       sorter=None, order=None):
    q = app.staffs.options(orm.undefer('context_labels')).filter(
        func.x_targets_match_ctxes(path_labels.get_targets(staff.uid, staff.context_labels), Staff.uid,
                                   Staff.context_labels))
    if uid is not None:
        q = q.filter_by(uid=uid)
    if context_label is not None:
        path, uids = context_label
        q = q.filter(func.x_target_match_ctxes(path, Staff.uid, Staff.context_labels))
        if len(uids) > 0 and uid is None:
            q = q.filter(Staff.uid.in_(uids))
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
