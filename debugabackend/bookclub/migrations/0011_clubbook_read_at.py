# Generated manually for historic reading order

from django.db import migrations, models


def backfill_read_at(apps, schema_editor):
    ClubBook = apps.get_model("bookclub", "ClubBook")
    for book in ClubBook.objects.filter(status="read", read_at__isnull=True):
        book.read_at = book.added_at
        book.save(update_fields=["read_at"])


class Migration(migrations.Migration):

    dependencies = [
        ("bookclub", "0010_alter_clubbook_google_books_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="clubbook",
            name="read_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When the book was first marked as read (historic).",
                null=True,
            ),
        ),
        migrations.RunPython(backfill_read_at, migrations.RunPython.noop),
    ]
