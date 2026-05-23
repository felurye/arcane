import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_models_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.client')),
            ],
        ),
        migrations.CreateModel(
            name='RagContext',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.JSONField()),
                ('tool_name', models.CharField(max_length=255)),
                ('tool_args', models.JSONField(blank=True, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.question')),
            ],
        ),
    ]
