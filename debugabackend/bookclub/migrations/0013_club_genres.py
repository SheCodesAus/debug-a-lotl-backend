from django.db import migrations, models


def default_empty_genre_list():
    return []


class Migration(migrations.Migration):

    dependencies = [
        ("bookclub", "0012_meeting_cancel_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="club",
            name="genres",
            field=models.JSONField(
                blank=True,
                default=default_empty_genre_list,
                help_text="Curated genre labels from the book categories list.",
            ),
        ),
    ]
