from django.db import migrations, models
from django.db.models import Q
from django.db.models.functions import Lower
import django.db.models.deletion
import core.models

class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.AddConstraint(model_name='user', constraint=models.UniqueConstraint(Lower('username'), name='monarch_username_ci_unique')),
        migrations.AddConstraint(model_name='user', constraint=models.UniqueConstraint(Lower('email'), condition=~Q(email=''), name='monarch_email_ci_unique')),
        migrations.CreateModel(name='PlayerPaths', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('modules', models.JSONField(default=core.models.default_modules)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='player_paths', to='core.user')),
        ]),
        migrations.CreateModel(name='SocialIdentity', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('provider', models.CharField(max_length=24)),
            ('subject', models.CharField(max_length=255)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_identities', to='core.user')),
        ], options={'constraints': [
            models.UniqueConstraint(fields=('provider','subject'), name='monarch_social_unique_subject'),
            models.UniqueConstraint(fields=('user','provider'), name='monarch_social_one_provider'),
        ]}),
    ]
