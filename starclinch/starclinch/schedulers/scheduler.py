from apscheduler.schedulers.background import BackgroundScheduler
from .task import *
# scheduler = BackgroundScheduler()
scheduler = BackgroundScheduler(max_instances=100, misfire_grace_time=600)

from apscheduler.schedulers.background import BackgroundScheduler
from .task import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_model_instance_scheduler(file_data, filename, attribute, instance):
    """
    Schedule a task to set the attribute of the specified instance with the provided file data.

    Args:
        file_data (bytes): Byte string representing the file data.
        filename (str): The filename for the uploaded file.
        attribute (str): The name of the attribute to be updated.
        instance (Model): The instance of the model to be updated.

    Returns:
        None
    """
    scheduler.add_job(create_model_instance_task, 'date', args=[file_data, filename, attribute, instance])



if not scheduler.running:
    scheduler.start()
    logger.info('Scheduler started')