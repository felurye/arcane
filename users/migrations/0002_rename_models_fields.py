import django.db.models
from django.db import migrations, models


def update_triage_values(apps, schema_editor):
    Client = apps.get_model('users', 'Client')
    mapping = {'verde': 'green', 'amarelo': 'yellow', 'laranja': 'orange', 'vermelho': 'red'}
    for old, new in mapping.items():
        Client.objects.filter(triage=old).update(triage=new)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel('Cliente', 'Client'),
        migrations.RenameModel('Consulta', 'Appointment'),

        migrations.RenameField('Client', 'nome', 'name'),
        migrations.RenameField('Client', 'telefone', 'phone'),
        migrations.RenameField('Client', 'especie', 'species'),
        migrations.RenameField('Client', 'nome_animal', 'animal_name'),
        migrations.RenameField('Client', 'raca', 'breed'),
        migrations.RenameField('Client', 'idade', 'age'),
        migrations.RenameField('Client', 'peso', 'weight'),
        migrations.RenameField('Client', 'triagem', 'triage'),

        migrations.RenameField('Appointment', 'cliente', 'client'),
        migrations.RenameField('Appointment', 'data', 'date'),
        migrations.RenameField('Appointment', 'observacao', 'observation'),
        migrations.RenameField('Appointment', 'transcricao', 'transcription'),
        migrations.RenameField('Appointment', 'segmentos', 'segments'),
        migrations.RenameField('Appointment', 'analise_exames', 'exam_analysis'),
        migrations.RenameField('Appointment', 'resumo', 'summary'),

        migrations.RunPython(update_triage_values, migrations.RunPython.noop),

        migrations.AlterField(
            model_name='client',
            name='triage',
            field=models.CharField(
                blank=True,
                choices=[('green', 'Verde'), ('yellow', 'Amarelo'), ('orange', 'Laranja'), ('red', 'Vermelho')],
                max_length=10,
                null=True,
            ),
        ),

        migrations.AlterField(
            model_name='client',
            name='species',
            field=models.CharField(
                choices=[('C', 'Cachorro'), ('G', 'Gato')],
                default='C',
                max_length=1,
            ),
        ),
    ]
