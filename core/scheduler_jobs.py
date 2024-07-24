from datetime import datetime

from core import scheduler
from core.models import TokenBlocklist


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
