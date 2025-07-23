from apis.recipemodel.models import *
from django.db.models import Q
from starclinch.utils import *

import io
from django.core.files.uploadedfile import InMemoryUploadedFile

def create_model_instance_task(file_data, filename, attribute, instance):
    """
    Set the attribute of the specified instance with the provided file data.

    Args:
        file_data (bytes): Byte string representing the file data.
        filename (str): The filename for the uploaded file.
        attribute (str): The name of the attribute to be updated.
        instance (Model): The instance of the model to be updated.

    Returns:
        None
    """
    try:
        file_object = InMemoryUploadedFile(io.BytesIO(file_data), None, filename, 'image/png', len(file_data), None)
        setattr(instance, attribute, file_object)
        instance.save()
    except Exception as e:
        print(f"An error occurred:")