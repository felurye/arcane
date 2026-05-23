from openai import OpenAI
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Appointment
from .agent import SummaryAgent, ExamAnalysisAgent, AssistantAgent


def transcribe_recording(appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    with open(appointment.video.path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            language="pt",
        )

    appointment.transcription = transcription.text
    appointment.save()
    return 'Ok'


def ocr_and_markdown_file(appointment_id):
    from docling.document_converter import DocumentConverter

    appointment = get_object_or_404(Appointment, id=appointment_id)

    converter = DocumentConverter()
    result = converter.convert(appointment.pdf.path)
    doc = result.document
    text = doc.export_to_markdown()

    appointment.ocr_pdf = text
    appointment.save()
    return 'Ok'


def summary_and_exam_analysis(appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    summary_agent = SummaryAgent()
    summary = summary_agent.run(appointment.transcription)
    appointment.summary = summary.summaries

    exam_analysis_agent = ExamAnalysisAgent()
    exam_analysis = exam_analysis_agent.run(appointment.ocr_pdf)
    appointment.exam_analysis = exam_analysis.analyses

    appointment.save()
    return 'Ok'


def rag_documents(appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    AssistantAgent.knowledge.insert(
        name=appointment.video.name,
        text_content=appointment.transcription,
        metadata={
            "paciente_id": appointment.client.id,
            "name": appointment.video.name,
            "tipo": "video",
        },
    )

    AssistantAgent.knowledge.insert(
        name=appointment.pdf.name,
        text_content=appointment.ocr_pdf,
        metadata={
            "paciente_id": appointment.client.id,
            "name": appointment.pdf.name,
        },
    )
