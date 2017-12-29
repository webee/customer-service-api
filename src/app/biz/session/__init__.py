from app.utils.commons import compose
from sqlalchemy import orm, desc, asc, func, or_
from sqlalchemy.sql.expression import nullslast, nullsfirst
from app.service.models import Session, Project, Staff, Customer
from time import time

order_func_map = {
    'ascend': compose(nullsfirst, asc),
    'descend': compose(nullslast, desc),
}


def staff_fetch_handling_sessions(app, staff, domain, type, page, per_page, user=None, handler=None, context_label=None,
                                  is_online=None,
                                  sorter=None, order=None):
    st = time()
    q = Session.query.join('project').options(orm.undefer('project.*')) \
        .filter(Session.is_active == True,
                Session.project.has(
                    app_name=app.name,
                    domain=domain, type=type),
                or_(
                    Session.handler_id == staff.id,
                    Session.project.has(
                        func.x_scopes_match_ctxes(
                            Project.scope_labels,
                            staff.uid,
                            staff.context_labels))
                )
                )
    if user is not None:
        q = q.filter(Session.project.has(Project.owner.has(uid=user)))
    if handler is not None:
        q = q.filter(Session.handler.has(uid=handler))
    if context_label is not None:
        path, uids = context_label
        q = q.filter(Session.project.has(func.x_scopes_match_target(Project.scope_labels, path)))
        if len(uids) > 0 and handler is None:
            q = q.filter(Session.handler.has(Staff.uid.in_(uids)))
    if is_online is not None:
        q = q.filter(Session.project.has(Project.is_online == is_online))

    order_func = order_func_map.get(order, order_func_map['descend'])
    if sorter is not None:
        if sorter == 'last_online_ts':
            q = q.order_by(order_func(Project.last_online_ts))
        elif sorter == 'created':
            q = q.order_by(order_func(Session.created))
        else:
            q = q.order_by(order_func(Session.updated))
    else:
        q = q.order_by(order_func(Session.updated))
    res = q.paginate(page, per_page, error_out=False, max_per_page=100)
    print('t: ', (time() - st) * 1000)
    return res
