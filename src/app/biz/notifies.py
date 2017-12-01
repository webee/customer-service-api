from app.task import tasks


def task_project_notify(project, type, details, handler=None):
    current_session = project.current_session
    handler = handler or current_session.handler
    if handler.is_online:
        details.update(dict(projectDomain=project.domain.name, projectType=project.type.name))
        tasks.notify_client.delay(handler.app_uid, 'project', type, details)


def task_app_notify(user, type, details):
    if user.is_online:
        tasks.notify_client.delay(user.app_uid, 'app', type, details)
