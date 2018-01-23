from app.utils.commons import compose
from sqlalchemy import orm, desc, asc, func, or_
from sqlalchemy.sql.expression import nullslast, nullsfirst
from app.service.models import Session, Project, Staff, Customer, Message

order_func_map = {
    'ascend': compose(nullsfirst, asc),
    'descend': compose(nullslast, desc),
}


def staff_fetch_handling_sessions(app, staff, domain, type, page, per_page, context_label=None,
                                  handler_context_label=None, leader_context_label=None, customer=None,
                                  owner=None, is_online=None, unhandled_msg_count_range=None, msg_ts_range=None,
                                  tag=None, handler_filter_self=None, leader_filter_self=None, sorter=None, order=None):
    q = _query_session(app, staff, domain, type, is_active=True, context_label=context_label,
                       handler_context_label=handler_context_label, leader_context_label=leader_context_label,
                       owner=owner, handler_filter_self=handler_filter_self, leader_filter_self=leader_filter_self,
                       tag=tag, is_online=is_online, customer=customer)

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


def staff_fetch_handled_sessions(app, staff, domain, type, page, per_page, context_label=None,
                                 handler_context_label=None, leader_context_label=None,
                                 owner=None, closed_ts_range=None, is_online=None, customer=None,
                                 tag=None, handler_filter_self=None, leader_filter_self=None, sorter=None, order=None):
    q = _query_session(app, staff, domain, type, is_active=False, context_label=context_label,
                       handler_context_label=handler_context_label, leader_context_label=leader_context_label,
                       owner=owner, handler_filter_self=handler_filter_self, leader_filter_self=leader_filter_self,
                       tag=tag, is_online=is_online, customer=customer)

    if closed_ts_range is not None:
        start, end = closed_ts_range
        if start is not None:
            q = q.filter(Session.msg.has(Message.ts >= start))
        if end is not None:
            q = q.filter(Session.msg.has(Message.ts <= end))

    order_func = order_func_map.get(order, order_func_map['descend'])
    if sorter is not None:
        if sorter == 'created':
            q = q.order_by(order_func(Session.created))
        elif sorter == 'closed':
            q = q.order_by(order_func(Session.closed))
        elif sorter == 'start_msg_id':
            q = q.order_by(order_func(Session.start_msg_id))
        else:
            q = q.order_by(order_func(Session.updated))
    else:
        q = q.order_by(order_func(Session.updated))
    res = q.paginate(page, per_page, error_out=False, max_per_page=100)
    return res


def _query_session(app, staff, domain, type, is_active, context_label=None, handler_context_label=None,
                   leader_context_label=None, owner=None, handler_filter_self=None, leader_filter_self=None, tag=None,
                   is_online=None, customer=None):
    q = Session.query.join('project').options(orm.undefer('project.*')) \
        .filter(Session.is_active == is_active,
                Session.project.has(
                    app_name=app.name,
                    domain=domain, type=type))

    filter_project_scopes = Session.project.has(
        func.x_scopes_match_ctxes(
            Project.scope_labels,
            staff.uid,
            staff.context_labels))

    leader_only_self = leader_filter_self == 'only'
    handler_only_self = handler_filter_self == 'only'
    if handler_only_self:
        # 仅自己接待的
        q = q.filter(Session.handler_id == staff.id)
        if leader_only_self:
            # 仅自己负责的
            q = q.filter(Session.project.has(leader_id=staff.id))
        elif leader_filter_self == 'exclude':
            # 排除自己负责的
            q = q.filter(Session.project.has(Project.leader_id != staff.id))
    elif handler_filter_self == 'exclude':
        # 排除自己接待的
        q = q.filter(Session.handler_id != staff.id)
        if leader_only_self:
            # 仅自己负责的
            q = q.filter(Session.project.has(leader_id=staff.id))
        elif leader_filter_self == 'exclude':
            # 排除自己负责的
            q = q.filter(Session.project.has(Project.leader_id != staff.id), filter_project_scopes)
        else:
            # 包含自己负责的
            q = q.filter(or_(Session.project.has(leader_id=staff.id), filter_project_scopes))
    else:
        # 包含自己接待的
        if leader_only_self:
            # 仅自己负责的
            q = q.filter(Session.project.has(leader_id=staff.id))
        elif leader_filter_self == 'exclude':
            # 排除自己负责的
            q = q.filter(Session.project.has(Project.leader_id != staff.id), filter_project_scopes)
        else:
            # 包含自己负责的
            q = q.filter(
                or_(
                    Session.handler_id == staff.id,
                    Session.project.has(leader_id=staff.id),
                    filter_project_scopes
                )
            )

    if context_label is not None:
        path, uids = context_label
        if len(uids) > 0:
            q = q.filter(Session.project.has(func.x_scopes_match_targets(Project.scope_labels, [path + uid for uid in uids])))
        else:
            q = q.filter(Session.project.has(func.x_scopes_match_target(Project.scope_labels, path)))

    if handler_context_label is not None:
        path, uids = handler_context_label
        q = q.filter(Session.handler.has(func.x_target_match_ctxes(path, Staff.uid, Staff.context_labels)))
        if len(uids) > 0 and not handler_only_self:
            q = q.filter(Session.handler.has(Staff.uid.in_(uids)))

    if leader_context_label is not None:
        path, uids = leader_context_label
        q = q.filter(
            Session.project.has(Project.leader.has(func.x_target_match_ctxes(path, Staff.uid, Staff.context_labels))))
        if len(uids) > 0 and not leader_filter_self:
            q = q.filter(Session.handler.has(Project.leader.has(Staff.uid.in_(uids))))

    if owner:
        s = f'%{owner}%'
        q = q.filter(Session.project.has(
            Project.owner.has(or_(Customer.name.like(s), Customer.mobile.like(s), Customer.uid.like(s)))))

    if customer:
        s = f'%{customer}%'
        q = q.filter(Session.project.has(
            Project.customers.any(or_(Customer.name.like(s), Customer.mobile.like(s), Customer.uid.like(s)))))

    if tag:
        s = f'%{tag}%'
        q = q.filter(Session.project.has(func.array_to_string(Project.tags, '*', ',').like(s)))

    if is_online is not None:
        q = q.filter(Session.project.has(Project.is_online == is_online))

    return q
