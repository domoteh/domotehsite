from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="provider",
            field=models.CharField(
                choices=[("monobank", "MonoBank"), ("cod", "Накладений платіж")],
                max_length=20,
                verbose_name="Провайдер",
            ),
        ),
    ]
