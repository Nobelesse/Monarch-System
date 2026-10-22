from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('core', '0002_accounts')]

    operations = [
        migrations.CreateModel(
            name='PlayerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, max_length=48)),
                ('timezone', models.CharField(default='Asia/Kolkata', max_length=64)),
                ('language', models.CharField(default='en', max_length=8)),
                ('reduced_motion', models.BooleanField(default=False)),
                ('high_contrast', models.BooleanField(default=False)),
                ('current_step', models.PositiveSmallIntegerField(default=1)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='onboarding_profile', to='core.user')),
            ],
        ),
        migrations.CreateModel(
            name='PrivatePhysique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height_cm', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('weight_kg', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='private_physique', to='core.user')),
            ],
        ),
        migrations.CreateModel(
            name='ModulePreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(max_length=12)),
                ('goal', models.CharField(blank=True, max_length=160)),
                ('experience', models.CharField(default='beginner', max_length=16)),
                ('equipment', models.JSONField(blank=True, default=list)),
                ('topics', models.JSONField(blank=True, default=list)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_preferences', to='core.user')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('user', 'module'), name='monarch_module_pref_unique')]},
        ),
        migrations.CreateModel(
            name='WeeklyAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(max_length=12)),
                ('weekday', models.PositiveSmallIntegerField()),
                ('minutes', models.PositiveSmallIntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_availability', to='core.user')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('user', 'module', 'weekday'), name='monarch_schedule_unique')]},
        ),
    ]
