from datetime import datetime

from core import scheduler
from core.models import TokenBlocklist, DeleteRequest, User


# test: ('interval', id='jwt_tokens_table_cleanup', seconds=60)
@scheduler.task("cron", id="jwt_tokens_table_cleanup", hour=0)
def cleanup_tokens_blocklist():
    with scheduler.app.app_context():
        current_time = datetime.utcnow()
        expired_tokens = TokenBlocklist.query.filter(
            TokenBlocklist.expired_at <= current_time
        ).all()

        if expired_tokens is not None:
            for token in expired_tokens:
                token.delete()


@scheduler.task("cron", id="delete_requests_check_up", hour=0)
def checkup_delete_requests():
    with scheduler.app.app_context():
        current_time = datetime.utcnow()

        expired_delete_request = DeleteRequest.query.filter(
            DeleteRequest.removed_at <= current_time
        ).all()

        if expired_delete_request is not None:
            for edr in expired_delete_request:
                User.query.filter_by(id=edr.user_id).delete()
                edr.delete()
