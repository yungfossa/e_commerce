from datetime import UTC, datetime

from core import scheduler
from core.models import DeleteRequest, TokenBlocklist, User


# test: ('interval', id='jwt_tokens_table_cleanup', seconds=60)
@scheduler.task("cron", id="jwt_tokens_table_cleanup", hour=0)
def cleanup_tokens_blocklist():
    """
    Scheduled task to clean up expired JWT tokens from the blocklist.

    This function runs daily at midnight (00:00) and removes all tokens
    from the TokenBlocklist that have expired. This helps to keep the
    blocklist table from growing indefinitely.

    Note: The commented out line below shows how this could be set up
    to run every 60 seconds for testing purposes.
    # test: ('interval', id='jwt_tokens_table_cleanup', seconds=60)
    """
    with scheduler.app.app_context():
        current_time = datetime.now(UTC)
        expired_tokens = TokenBlocklist.query.filter(
            TokenBlocklist.expired_at <= current_time
        ).all()

        if expired_tokens is not None:
            for token in expired_tokens:
                token.delete()


@scheduler.task("cron", id="delete_requests_cleanup", hour=0)
def cleanup_delete_requests():
    """
    Scheduled task to process and execute user deletion requests.

    This function runs daily at midnight (00:00) and checks for any
    DeleteRequest entries where the scheduled deletion time
    (to_be_removed_at) has passed. For each such request, it deletes
    the associated user account and then removes the DeleteRequest entry.

    This implementation allows for a grace period between when a user
    requests account deletion and when it actually occurs, giving users
    a chance to change their minds.
    """
    with scheduler.app.app_context():
        current_time = datetime.now(UTC)

        expired_delete_request = DeleteRequest.query.filter(
            DeleteRequest.to_be_removed_at <= current_time
        ).all()

        if expired_delete_request is not None:
            for edr in expired_delete_request:
                User.query.filter_by(id=edr.user_id).delete()
                edr.delete()


# This module defines scheduled tasks for the application using Flask-APScheduler.
# These tasks perform regular maintenance operations:
# 1. Cleaning up expired JWT tokens from the blocklist
# 2. Processing and executing user account deletion requests

# Both tasks are scheduled to run daily at midnight (00:00) UTC.
# The scheduler ensures these maintenance tasks occur regularly without manual intervention,
# helping to keep the database clean and respect user privacy requests.
