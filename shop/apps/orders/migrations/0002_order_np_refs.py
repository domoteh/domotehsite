from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="nova_poshta_city_ref",
            field=models.CharField(blank=True, max_length=36, verbose_name="Ref міста НП"),
        ),
        migrations.AddField(
            model_name="order",
            name="nova_poshta_warehouse_ref",
            field=models.CharField(blank=True, max_length=36, verbose_name="Ref відділення НП"),
        ),
        migrations.AlterField(
            model_name="order",
            name="nova_poshta_warehouse",
            field=models.CharField(blank=True, max_length=500, verbose_name="Відділення НП"),
        ),
    ]
