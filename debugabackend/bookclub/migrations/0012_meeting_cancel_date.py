from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookclub", "0011_clubbook_read_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="cancel_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
