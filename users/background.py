from users.utils import unmark_positive_user
from celery import Celery
from celery.schedules import crontab
from users.database import db, User
from celery.utils.log import get_task_logger
import datetime

logger = get_task_logger(__name__)

celery = Celery()
_APP = None

@celery.task
def unmark():
    """
    Search all positive users and 
    for those who have been positive for more than 14 days 
    marks them as negative
    """
    with _APP.app_context():
        now = datetime.datetime.now()
        users = db.session.query(User)\
        .filter_by(is_positive = True)\
        .all() 

        negatives = []
        for u in users:
            if u.positive_datetime+datetime.timedelta(days=14) <= now:
                negatives.append(u)
                unmark_positive_user(u.id)

        logger.info(negatives)

def init_celery(app, worker=False):
    #print(app.config,flush=True)
    # load celery config
    celery.config_from_object(app.config)
    global _APP
    _APP = app
    if not worker:
        # Config for non-worker related settings
        pass