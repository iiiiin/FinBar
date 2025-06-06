# Generated by Django 4.2.21 on 2025-05-25 12:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MarkedVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('videoId', models.CharField(max_length=100)),
                ('channelTitle', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('thumbnailURL', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='markedvideo',
            constraint=models.UniqueConstraint(fields=('user_id', 'videoId'), name='Marked_video'),
        ),
    ]
