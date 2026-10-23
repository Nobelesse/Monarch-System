
from django.db import migrations, models
import django.db.models.deletion

CATALOG = [('chair-sit-to-stand', 'Chair sit-to-stand', 'squat', 'bodyweight', 'beginner', ['knee'], 'Stand up from a stable chair with control; sit back down slowly.'), ('supported-shallow-squat', 'Supported shallow squat', 'squat', 'bodyweight', 'beginner', ['knee'], 'Hold a stable support; bend only as far as comfortable, then stand tall.'), ('goblet-squat', 'Goblet squat', 'squat', 'dumbbells', 'intermediate', ['knee'], 'Hold a light dumbbell close to chest; squat with a controlled range.'), ('gym-leg-press', 'Seated leg press', 'squat', 'gym', 'intermediate', ['knee'], 'Set a comfortable range and light resistance; avoid locking knees.'), ('standing-hip-hinge', 'Standing hip hinge', 'hinge', 'bodyweight', 'beginner', [], 'Soften knees, move hips backward, and return upright with control.'), ('glute-bridge', 'Glute bridge', 'hinge', 'bodyweight', 'beginner', ['floor'], 'Lie on your back, press through feet, and raise hips without arching.'), ('dumbbell-romanian-deadlift', 'Light dumbbell hip hinge', 'hinge', 'dumbbells', 'intermediate', [], 'Hold light weights near legs; hinge at hips without rounding your back.'), ('kettlebell-deadlift', 'Kettlebell deadlift', 'hinge', 'kettlebell', 'intermediate', [], 'Start with bell between feet; hinge back and stand with controlled tempo.'), ('wall-pushup', 'Wall push-up', 'push', 'bodyweight', 'beginner', ['wrist'], 'Press away from a wall, keeping a straight body line.'), ('incline-pushup', 'Incline push-up', 'push', 'bodyweight', 'beginner', ['wrist'], 'Place hands on a stable raised surface; lower and press slowly.'), ('floor-pushup', 'Floor push-up', 'push', 'bodyweight', 'intermediate', ['floor', 'wrist'], 'Use a comfortable range and steady pace; keep body aligned.'), ('dumbbell-floor-press', 'Dumbbell floor press', 'push', 'dumbbells', 'intermediate', ['floor', 'wrist'], 'Lie on the floor and press light weights with controlled elbows.'), ('seated-chest-press', 'Seated chest press', 'push', 'gym', 'beginner', ['wrist'], 'Adjust the machine and use light resistance without forcing the range.'), ('shoulder-blade-squeeze', 'Standing shoulder-blade squeeze', 'pull', 'bodyweight', 'beginner', [], 'Draw shoulder blades gently together; pause and release.'), ('prone-w-raise', 'Prone W raise', 'pull', 'bodyweight', 'intermediate', ['floor'], 'Lie face down and lift bent arms slightly without straining neck.'), ('band-row', 'Resistance band row', 'pull', 'resistance_bands', 'beginner', ['wrist'], 'Anchor the band securely and draw elbows backward under control.'), ('dumbbell-row', 'Supported dumbbell row', 'pull', 'dumbbells', 'intermediate', ['wrist'], 'Brace on a stable support and pull a light dumbbell toward hip.'), ('seated-cable-row', 'Seated cable row', 'pull', 'gym', 'intermediate', ['wrist'], 'Keep torso stable and bring handles toward ribs with control.'), ('standing-brace', 'Standing abdominal brace', 'core', 'bodyweight', 'beginner', [], 'Breathe normally while gently tightening your trunk for a few seconds.'), ('dead-bug', 'Dead bug', 'core', 'bodyweight', 'beginner', ['floor'], 'Lie on back and slowly extend opposite limbs while keeping trunk stable.'), ('bird-dog', 'Bird dog', 'core', 'bodyweight', 'beginner', ['floor', 'wrist'], 'On hands and knees, slowly extend opposite arm and leg.'), ('side-plank-knees', 'Side plank on knees', 'core', 'bodyweight', 'intermediate', ['floor', 'wrist'], 'Support from forearm and knees; lift hips gently and hold.'), ('standing-calf-mobility', 'Supported calf mobility', 'mobility', 'bodyweight', 'beginner', [], 'Use a stable support; move ankles through a comfortable range.'), ('seated-shoulder-circles', 'Seated shoulder circles', 'mobility', 'bodyweight', 'beginner', [], 'Make slow, comfortable circles with shoulders without forcing motion.'), ('standing-side-reach', 'Standing side reach', 'mobility', 'bodyweight', 'beginner', ['overhead'], 'Reach upward gently to one side and return to center.'), ('seated-thoracic-rotation', 'Seated upper-back rotation', 'mobility', 'bodyweight', 'beginner', [], 'Sit upright and turn upper torso slowly within a comfortable range.'), ('gentle-march', 'Gentle march in place', 'mobility', 'bodyweight', 'beginner', ['impact', 'knee'], 'March gently while staying near a stable support if needed.'), ('ankle-circles', 'Seated ankle circles', 'mobility', 'bodyweight', 'beginner', [], 'Move each ankle slowly in a comfortable circle while seated.')]


def seed_exercises(apps, schema_editor):
    Exercise = apps.get_model('core', 'WorkoutExercise')
    for slug, name, movement, equipment, level, tags, instructions in CATALOG:
        Exercise.objects.update_or_create(slug=slug, defaults={
            'name': name, 'movement': movement, 'equipment': equipment,
            'minimum_level': level, 'caution_tags': tags, 'instructions': instructions,
            'active': True,
        })


def unseed(apps, schema_editor):
    Exercise = apps.get_model('core', 'WorkoutExercise')
    Exercise.objects.filter(slug__in=[row[0] for row in CATALOG]).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0003_onboarding')]
    operations = [
        migrations.CreateModel(name='WorkoutExercise', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('slug', models.SlugField(max_length=72, unique=True)),
            ('name', models.CharField(max_length=90)),
            ('movement', models.CharField(max_length=16)),
            ('equipment', models.CharField(default='bodyweight', max_length=24)),
            ('minimum_level', models.CharField(default='beginner', max_length=16)),
            ('caution_tags', models.JSONField(default=list)),
            ('instructions', models.CharField(max_length=250)),
            ('active', models.BooleanField(default=True)),
        ], options={'ordering': ['name']}),
        migrations.CreateModel(name='WorkoutPlan', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('source_signature', models.CharField(max_length=64)),
            ('goal_snapshot', models.CharField(max_length=160)),
            ('experience_snapshot', models.CharField(max_length=16)),
            ('equipment_snapshot', models.JSONField(default=list)),
            ('avoid_tags', models.JSONField(default=list)),
            ('generated_at', models.DateTimeField(auto_now=True)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='workout_plan', to='core.user')),
        ]),
        migrations.CreateModel(name='WorkoutSession', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('weekday', models.PositiveSmallIntegerField()),
            ('available_minutes', models.PositiveSmallIntegerField()),
            ('planned_minutes', models.PositiveSmallIntegerField()),
            ('focus', models.CharField(max_length=16)),
            ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='core.workoutplan')),
        ], options={'ordering': ['weekday']}),
        migrations.CreateModel(name='WorkoutPlanItem', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('position', models.PositiveSmallIntegerField()),
            ('sets', models.PositiveSmallIntegerField()),
            ('reps', models.CharField(max_length=30)),
            ('rest_seconds', models.PositiveSmallIntegerField()),
            ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.workoutexercise')),
            ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.workoutsession')),
        ], options={'ordering': ['position']}),
        migrations.AddConstraint(model_name='workoutsession', constraint=models.UniqueConstraint(fields=('plan', 'weekday'), name='monarch_workout_unique_day')),
        migrations.AddConstraint(model_name='workoutplanitem', constraint=models.UniqueConstraint(fields=('session', 'position'), name='monarch_workout_unique_position')),
        migrations.RunPython(seed_exercises, migrations.RunPython.noop),
    ]
