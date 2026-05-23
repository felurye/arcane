from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import Chain

from .models import Appointment
from .tasks import transcribe_recording, ocr_and_markdown_file, summary_and_exam_analysis, rag_documents


@receiver(post_save, sender=Appointment)
def handle_new_appointment(sender, instance, created, **kwargs):
    if created:
        chain = Chain()
        chain.append(transcribe_recording, instance.id)
        chain.append(ocr_and_markdown_file, instance.id)
        chain.append(summary_and_exam_analysis, instance.id)
        chain.append(rag_documents, instance.id)
        chain.run()
