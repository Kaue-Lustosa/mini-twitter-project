# Generated by Django 4.2.7 on 2025-05-05 02:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hashtag',
            name='post_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='is_reply',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='is_retweet',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='original_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retweets', to='posts.post'),
        ),
        migrations.AddField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='posts.post'),
        ),
        migrations.AddField(
            model_name='post',
            name='replies_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='retweets_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Retweet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retweeted_by', to='posts.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retweets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'post')},
            },
        ),
        migrations.CreateModel(
            name='Mention',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentions', to='posts.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentioned_in', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('post', 'user')},
            },
        ),
    ]
