from django.db import models


class Cliente(models.Model):
    especie_choices = [
        ('C', 'Cachorro'),
        ('G', 'Gato'),
    ]
    raca_choices = [
        ('SRD', 'SRD'),
        ('Labrador', 'Labrador'),
    ]
    triagem_choices = [
        ('verde', 'Verde'),
        ('amarelo', 'Amarelo'),
        ('laranja', 'Laranja'),
        ('vermelho', 'Vermelho'),
    ]
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    especie = models.CharField(max_length=1, choices=especie_choices, default='C')
    nome_animal = models.CharField(max_length=100, null=True, blank=True)
    raca = models.CharField(max_length=100, null=True, blank=True)
    idade = models.IntegerField(null=True, blank=True)
    peso = models.FloatField(null=True, blank=True)
    triagem = models.CharField(max_length=10, choices=triagem_choices, null=True, blank=True)

    def __str__(self):
        return self.nome


class Consulta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)
    transcricao = models.TextField(null=True, blank=True)
    segmentos = models.JSONField(null=True, blank=True)
    ocr_pdf = models.TextField(null=True, blank=True)
    analise_exames = models.JSONField(null=True, blank=True)
    resumo = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.cliente.nome


class Pergunta(models.Model):
    pergunta = models.TextField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return self.pergunta


class ContextRag(models.Model):
    content = models.JSONField()
    tool_name = models.CharField(max_length=255)
    tool_args = models.JSONField(null=True, blank=True)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)

    def __str__(self):
        return self.tool_name
