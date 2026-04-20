from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_objeto_status'),
    ]

    def apagar_encerrados(apps, schema_editor):
        Objeto = apps.get_model('core', 'Objeto')
        Objeto.objects.filter(status='encerrado').delete()

    operations = [
        migrations.RunPython(apagar_encerrados, migrations.RunPython.noop),
    ]
