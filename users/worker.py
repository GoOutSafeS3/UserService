from celery import Celery
from celery.schedules import crontab

from users.app import create_worker_app
from users.background import unmark

def create_celery(app):

    celery = Celery(
        app.import_name,
        backend=app.config["result_backend"],
        broker=app.config["broker_url"],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = create_worker_app()
celery = create_celery(app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.add_periodic_task(2, unmark.s(), name=f"Unmark positive users | a controll each {app.config['UNMARK_AFTER']} seconds")