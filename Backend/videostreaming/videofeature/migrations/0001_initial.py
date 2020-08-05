# Generated by Django 2.2.11 on 2020-04-01 16:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VideoUploadRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.TextField()),
                ('is_bucket_path', models.BooleanField(default=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='UserManagement',
            fields=[
                ('id', models.AutoField(default=None, primary_key=True, serialize=False)),
                ('firstName', models.TextField(default=None, max_length=25)),
                ('lastName', models.TextField(default=None, max_length=25)),
                ('username', models.TextField(default=None, max_length=50)),
                ('password', models.TextField(default=None)),
                ('signUpDate', models.DateTimeField(auto_now_add=True)),
                ('email', models.TextField(default=None, max_length=40)),
                ('isSubscribed', models.SmallIntegerField(default=None, max_length=4)),
            ],
            options={
                'db_table': 'user_credentials',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='VideoDetails',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('video_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('video_name', models.TextField()),
                ('video_description', models.TextField(blank=True, null=True)),
                ('thumbnail_url', models.TextField(blank=True, null=True)),
                ('video_duration', models.BigIntegerField(null=True)),
                ('video_category', models.CharField(max_length=100, null=True)),
                ('video_resolution', models.CharField(max_length=12, null=True)),
                ('video_encoding', models.CharField(max_length=12, null=True)),
                ('video_path', models.TextField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('video_size', models.BigIntegerField(null=True)),
                ('video_count', models.BigIntegerField(default=0, null=True)),
                ('clip_url', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'video_details',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='VideoEncodingFormat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('encoding_type', models.TextField(blank=True, max_length=10, null=True)),
                ('resolution', models.TextField(blank=True, max_length=10, null=True)),
            ],
            options={
                'db_table': 'video_encoding_formats',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='VideoUserTable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('duration', models.TextField(blank=True, null=True)),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='videofeature.UserManagement')),
                ('video_id', models.ForeignKey(db_column='video_id', on_delete=django.db.models.deletion.CASCADE, to='videofeature.VideoDetails')),
            ],
            options={
                'db_table': 'video_transcation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='VideoEncodingDetails',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('video_path', models.TextField(blank=True, null=True)),
                ('encoding_id', models.ForeignKey(db_column='encoding_id', on_delete=django.db.models.deletion.CASCADE, to='videofeature.VideoEncodingFormat')),
                ('video_id', models.ForeignKey(db_column='video_id', on_delete=django.db.models.deletion.CASCADE, to='videofeature.VideoDetails')),
            ],
            options={
                'db_table': 'encoded_video_details',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='VideoEncoding',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('video_encoding', models.CharField(max_length=12, null=True)),
                ('video_resolution', models.CharField(max_length=12, null=True)),
                ('video_path', models.TextField(blank=True, null=True)),
                ('video_thumbnail', models.TextField(blank=True, null=True)),
                ('video_id', models.ForeignKey(db_column='video_id', on_delete=django.db.models.deletion.CASCADE, to='videofeature.VideoDetails')),
            ],
            options={
                'db_table': 'video_encoding',
                'managed': True,
            },
        ),
    ]