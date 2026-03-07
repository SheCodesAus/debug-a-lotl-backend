# Generated manually for User_Club schema (role: Owner/Member, status: Pending/Approved/Rejected)

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def backfill_owners(apps, schema_editor):
    """Create Owner membership for each existing club's creator."""
    Club = apps.get_model("bookclub", "Club")
    UserClub = apps.get_model("bookclub", "UserClub")
    for club in Club.objects.all():
        UserClub.objects.get_or_create(
            user=club.created_by,
            club=club,
            defaults={"role": "owner", "status": "approved"},
        )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bookclub", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserClub",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("owner", "Owner"), ("member", "Member")], max_length=20)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], max_length=20)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("club", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="bookclub.club")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="club_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-joined_at"],
                "verbose_name": "User-Club membership",
                "unique_together": {("user", "club")},
            },
        ),
        migrations.RunPython(backfill_owners, migrations.RunPython.noop),
    ]
