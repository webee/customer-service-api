from app.utils.commons import compose
from sqlalchemy import orm, desc, asc, func, or_
from sqlalchemy.sql.expression import nullslast, nullsfirst
from app.service.models import Session, Project, Staff, Customer, Message

order_func_map = {
    'ascend': compose(nullsfirst, asc),
    'descend': compose(nullslast, desc),
}


def staff_fetch_handling_sessions(app, staff, domain, type, page, per_page, context_label=None, handler=None,
                                  owner=None, is_online=None, unhandled_msg_count_range=None, msg_ts_range=None,
                                  tag=None, exclude_self=None, sorter=None, order=None):
    q = Session.query.join('project').options(orm.undefer('project.*')) \
        .filter(Session.is_active == True,
                Session.project.has(
                    app_name=app.name,
                    domain=domain, type=type))
    if owner is not None:
        s = f'%{owner}%'
        q = q.filter(Session.project.has(
            Project.owner.has(or_(Customer.name.like(s), Customer.mobile.like(s), Customer.uid.like(s)))))

    if exclude_self:
        q = q.filter(
            or_(
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )
    else:
        q = q.filter(
            or_(
                Session.handler_id == staff.id,
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )

    if handler is not None:
        q = q.filter(Session.handler.has(uid=handler))
    elif exclude_self:
        q = q.filter(Session.handler_id != staff.id)

    if context_label is not None:
        path, uids = context_label
        q = q.filter(Session.project.has(func.x_scopes_match_target(Project.scope_labels, path)))
        if len(uids) > 0 and handler is None:
            q = q.filter(Session.handler.has(Staff.uid.in_(uids)))

    if unhandled_msg_count_range is not None:
        start, end = unhandled_msg_count_range
        if start is not None:
            q = q.filter(Session.unhandled_count >= start)
        if end is not None:
            q = q.filter(Session.unhandled_count <= end)

    if msg_ts_range is not None:
        start, end = msg_ts_range
        if start is not None:
            q = q.filter(Session.msg.has(Message.ts >= start))
        if end is not None:
            q = q.filter(Session.msg.has(Message.ts <= end))

    if tag is not None:
        q = q.filter(Session.project.has(func.array_to_string(Project.tags, '*', ',').like('%')))

    if is_online is not None:
        q = q.filter(Session.project.has(Project.is_online == is_online))

    order_func = order_func_map.get(order, order_func_map['descend'])
    if sorter is not None:
        if sorter == 'last_online_ts':
            q = q.order_by(order_func(Project.last_online_ts))
        elif sorter == 'created':
            q = q.order_by(order_func(Session.created))
        elif sorter == 'unsynced_count':
            q = q.order_by(order_func(Session.unsynced_count))
        elif sorter == 'unhandled_count':
            q = q.order_by(order_func(Session.unhandled_count))
        elif sorter == 'msg_count':
            q = q.order_by(order_func(Session.msg_count))
        else:
            q = q.order_by(order_func(Session.updated))
    else:
        q = q.order_by(order_func(Session.updated))
    res = q.paginate(page, per_page, error_out=False, max_per_page=100)
    return res


def staff_fetch_handled_sessions(app, staff, domain, type, page, per_page, context_label=None, handler=None,
                                 owner=None, closed_ts_range=None,
                                 tag=None, exclude_self=None, sorter=None, order=None):
    q = Session.query.join('project').options(orm.undefer('project.*')) \
        .filter(Session.is_active == False,
                Session.project.has(
                    app_name=app.name,
                    domain=domain, type=type))
    if owner is not None:
        s = f'%{owner}%'
        q = q.filter(Session.project.has(
            Project.owner.has(or_(Customer.name.like(s), Customer.mobile.like(s), Customer.uid.like(s)))))

    if exclude_self:
        q = q.filter(
            or_(
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )
    else:
        q = q.filter(
            or_(
                Session.handler_id == staff.id,
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )

    if handler is not None:
        q = q.filter(Session.handler.has(uid=handler))
    elif exclude_self:
        q = q.filter(Session.handler_id != staff.id)

    if context_label is not None:
        path, uids = context_label
        q = q.filter(Session.project.has(func.x_scopes_match_target(Project.scope_labels, path)))
        if len(uids) > 0 and handler is None:
            q = q.filter(Session.handler.has(Staff.uid.in_(uids)))

    if closed_ts_range is not None:
        start, end = closed_ts_range
        if start is not None:
            q = q.filter(Session.msg.has(Message.ts >= start))
        if end is not None:
            q = q.filter(Session.msg.has(Message.ts <= end))

    if tag is not None:
        q = q.filter(Session.project.has(func.array_to_string(Project.tags, '*', ',').like('%')))

    order_func = order_func_map.get(order, order_func_map['descend'])
    if sorter is not None:
        if sorter == 'created':
            q = q.order_by(order_func(Session.created))
        else:
            q = q.order_by(order_func(Session.updated))
    else:
        q = q.order_by(order_func(Session.updated))
    res = q.paginate(page, per_page, error_out=False, max_per_page=100)
    return res


def staff_fetch_handled_sessions(app, staff, domain, type, page, per_page, context_label=None, handler=None,
                                 owner=None, is_online=None, unhandled_msg_count_range=None, msg_ts_range=None,
                                 tag=None, exclude_self=None, sorter=None, order=None):
    q = Session.query.join('project').options(orm.undefer('project.*')) \
        .filter(Session.is_active == True,
                Session.project.has(
                    app_name=app.name,
                    domain=domain, type=type))
    if owner is not None:
        s = f'%{owner}%'
        q = q.filter(Session.project.has(
            Project.owner.has(or_(Customer.name.like(s), Customer.mobile.like(s), Customer.uid.like(s)))))

    if exclude_self:
        q = q.filter(
            or_(
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )
    else:
        q = q.filter(
            or_(
                Session.handler_id == staff.id,
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )

    if handler is not None:
        q = q.filter(Session.handler.has(uid=handler))
    elif exclude_self:
        q = q.filter(Session.handler_id != staff.id)

    if context_label is not None:
        path, uids = context_label
        q = q.filter(Session.project.has(func.x_scopes_match_target(Project.scope_labels, path)))
        if len(uids) > 0 and handler is None:
            q = q.filter(Session.handler.has(Staff.uid.in_(uids)))

    if unhandled_msg_count_range is not None:
        start, end = unhandled_msg_count_range
        if start is not None:
            q = q.filter(Session.unhandled_count >= start)
        if end is not None:
            q = q.filter(Session.unhandled_count <= end)

    if msg_ts_range is not None:
        start, end = msg_ts_range
        if start is not None:
            q = q.filter(Session.msg.has(Message.ts >= start))
        if end is not None:
            q = q.filter(Session.msg.has(Message.ts <= end))

    if tag is not None:
        q = q.filter(Session.project.has(func.array_to_string(Project.tags, '*', ',').like('%')))

    if is_online is not None:
        q = q.filter(Session.project.has(Project.is_online == is_online))

    order_func = order_func_map.get(order, order_func_map['descend'])
    if sorter is not None:
        if sorter == 'last_online_ts':
            q = q.order_by(order_func(Project.last_online_ts))
        elif sorter == 'created':
            q = q.order_by(order_func(Session.created))
        elif sorter == 'unsynced_count':
            q = q.order_by(order_func(Session.unsynced_count))
        elif sorter == 'unhandled_count':
            q = q.order_by(order_func(Session.unhandled_count))
        elif sorter == 'msg_count':
            q = q.order_by(order_func(Session.msg_count))
        else:
            q = q.order_by(order_func(Session.updated))
    else:
        q = q.order_by(order_func(Session.updated))
    res = q.paginate(page, per_page, error_out=False, max_per_page=100)
    return res


def staff_fetch_handled_sessions(app, staff, domain, type, page, per_page, context_label=None, handler=None,
                                 owner=None, closed_ts_range=None,
                                 tag=None, exclude_self=None, sorter=None, order=None):
    q = Session.query.join('project').options(orm.undefer('project.*')) \
        .filter(Session.is_active == False,
                Session.project.has(
                    app_name=app.name,
                    domain=domain, type=type))
    if owner is not None:
        s = f'%{owner}%'
        q = q.filter(Session.project.has(
            Project.owner.has(or_(Customer.name.like(s), Customer.mobile.like(s), Customer.uid.like(s)))))

    if exclude_self:
        q = q.filter(
            or_(
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )
    else:
        q = q.filter(
            or_(
                Session.handler_id == staff.id,
                Session.project.has(leader_id=staff.id),
                Session.project.has(
                    func.x_scopes_match_ctxes(
                        Project.scope_labels,
                        staff.uid,
                        staff.context_labels))
            )
        )

    if handler is not None:
        q = q.filter(Session.handler.has(uid=handler))
    elif exclude_self:
        q = q.filter(Session.handler_id != staff.id)

    if context_label is not None:
        path, uids = context_label
        q = q.filter(Session.project.has(func.x_scopes_match_target(Project.scope_labels, path)))
        if len(uids) > 0 and handler is None:
            q = q.filter(Session.handler.has(Staff.uid.in_(uids)))

    if closed_ts_range is not None:
        start, end = closed_ts_range
        if start is not None:
            q = q.filter(Session.msg.has(Message.ts >= start))
        if end is not None:
            q = q.filter(Session.msg.has(Message.ts <= end))

    if tag is not None:
        q = q.filter(Session.project.has(func.array_to_string(Project.tags, '*', ',').like('%')))

    order_func = order_func_map.get(order, order_func_map['descend'])
    if sorter is not None:
        if sorter == 'created':
            q = q.order_by(order_func(Session.created))
        else:
            q = q.order_by(order_func(Session.updated))
    else:
        q = q.order_by(order_func(Session.updated))
    res = q.paginate(page, per_page, error_out=False, max_per_page=100)
    return res
