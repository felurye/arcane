from django.db import models


class Client(models.Model):
    SPECIES_CHOICES = [
        ('C', 'Cachorro'),
        ('G', 'Gato'),
    ]
    BREED_CHOICES = [
        ('SRD', 'SRD'),
        ('Labrador', 'Labrador'),
    ]
    TRIAGE_CHOICES = [
        ('green', 'Verde'),
        ('yellow', 'Amarelo'),
        ('orange', 'Laranja'),
        ('red', 'Vermelho'),
    ]
    name = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    species = models.CharField(max_length=1, choices=SPECIES_CHOICES, default='C')
    animal_name = models.CharField(max_length=100, null=True, blank=True)
    breed = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    triage = models.CharField(max_length=10, choices=TRIAGE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    observation = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)
    segments = models.JSONField(null=True, blank=True)
    ocr_pdf = models.TextField(null=True, blank=True)
    exam_analysis = models.JSONField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.client.name


class Question(models.Model):
    text = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class RagContext(models.Model):
    content = models.JSONField()
    tool_name = models.CharField(max_length=255)
    tool_args = models.JSONField(null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.tool_name
