import logging
import time

from app.service.models import Project, ProjectXChat

logger = logging.getLogger(__name__)


def syncing_proj_xchat_msgs(syncing, sync_proj_xchat_msgs_func, proj_id=None, proj_xchat_id=None, proj=None,
                            proj_xchat=None, acc_time=0.12, done_syncing_func=None, extra_sync_kwargs=None):
    if proj is not None:
        proj_xchat_id = proj.xchat.id
    elif proj_xchat is not None:
        proj = proj_xchat.project
        proj_xchat_id = proj_xchat.id
    elif proj_id is not None:
        proj = Project.query.filter_by(id=proj_id).one()
        proj_xchat_id = proj.xchat.id
    elif proj_xchat_id is not None:
        proj_xchat = ProjectXChat.query.filter_by(id=proj_xchat_id).one()
        proj = proj_xchat.project
        proj_xchat_id = proj_xchat.id
    else:
        return

    if ProjectXChat.try_sync(proj_xchat_id, syncing=syncing):
        try:
            synced_count = 0
            while True:
                pending = ProjectXChat.current_pending(proj_xchat_id, syncing)
                synced_count += sync_proj_xchat_msgs_func(proj, **(extra_sync_kwargs or {}))
                extra_sync_kwargs = {}
                if not ProjectXChat.done_sync(proj_xchat_id, cur_pending=pending, syncing=syncing):
                    # 延时累积
                    time.sleep(acc_time)
                    continue
                break
            if done_syncing_func:
                done_syncing_func(synced_count, proj)
        except:
            logger.exception('sync xchat msg error: %d', proj_xchat_id)
            ProjectXChat.stop_sync(proj_xchat_id, syncing=syncing)
