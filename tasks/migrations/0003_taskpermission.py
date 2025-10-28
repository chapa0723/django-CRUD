# Generated manually for permissions system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0002_rename_datedcompleted_task_datecompleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='owned_tasks',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-created'], 'verbose_name': 'Tarea', 'verbose_name_plural': 'Tareas'},
        ),
        migrations.CreateModel(
            name='TaskPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_view', models.BooleanField(default=True, verbose_name='Puede Ver')),
                ('can_edit', models.BooleanField(default=False, verbose_name='Puede Editar')),
                ('can_delete', models.BooleanField(default=False, verbose_name='Puede Eliminar')),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('granted_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='granted_permissions',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Concedido por'
                )),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_permissions', to='tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Permiso de Tarea',
                'verbose_name_plural': 'Permisos de Tareas',
            },
        ),
        migrations.AlterUniqueTogether(
            name='taskpermission',
            unique_together={('task', 'user')},
        ),
    ]

