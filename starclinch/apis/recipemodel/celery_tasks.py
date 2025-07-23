from celery import shared_task
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from django.apps import apps
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
import logging

logger = logging.getLogger(__name__)


@shared_task
def save_resized_image_task(file_data, filename, attribute, model_name, instance_id):
    try:
        ModelClass = apps.get_model('recipemodel', model_name)
        if not ModelClass:
            logger.warning(f"[Celery Task Error] Model '{model_name}' not found.")
            return

        instance = ModelClass.objects.get(pk=instance_id)
        image = Image.open(io.BytesIO(file_data)).convert("RGB")  
        image.thumbnail((800, 800))

        output_format = 'WEBP' 
        new_filename = filename.rsplit('.', 1)[0] + f'.{output_format.lower()}'

        buffer = BytesIO()
        image.save(buffer, format=output_format, quality=85, optimize=True)
        buffer.seek(0)

        file_object = InMemoryUploadedFile(
            buffer, None, new_filename, f'image/{output_format.lower()}', buffer.getbuffer().nbytes, None
        )

        setattr(instance, attribute, file_object)
        instance.save()

    except Exception as e:
        logger.warning(f"[Celery Task Error] Failed to save resized image: {e}")
