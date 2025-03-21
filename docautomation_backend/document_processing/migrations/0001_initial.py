# Generated by Django 4.2.20 on 2025-03-07 13:33

from django.db import migrations, models
import document_processing.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=document_processing.models.document_file_path)),
                ('document_type', models.CharField(choices=[('pdf', 'PDF'), ('docx', 'DOCX'), ('txt', 'Text'), ('image', 'Image'), ('other', 'Other')], default='other', max_length=10)),
                ('extracted_text', models.TextField(blank=True)),
                ('metadata', models.JSONField(blank=True, default=dict, null=True)),
                ('processing_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
