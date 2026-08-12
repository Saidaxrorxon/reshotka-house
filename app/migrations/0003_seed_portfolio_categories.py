from django.db import migrations

CATEGORIES = [
    ("Решётки", "grilles"),
    ("Перила", "railings"),
    ("Навесы", "canopies"),
    ("Ворота", "gates"),
    ("Заборы", "fences"),
    ("Каркасные ангары", "hangars"),
]


def seed_categories(apps, schema_editor):
    PortfolioCategory = apps.get_model("app", "PortfolioCategory")
    for name, slug in CATEGORIES:
        category, created = PortfolioCategory.objects.get_or_create(
            name=name, defaults={"slug": slug}
        )
        if not created and category.slug != slug:
            category.slug = slug
            category.save(update_fields=["slug"])


def noop_reverse(apps, schema_editor):
    # Deliberately not deleting categories on reverse - they may already
    # have real portfolio items attached by the time this is rolled back.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_review"),
    ]

    operations = [
        migrations.RunPython(seed_categories, noop_reverse),
    ]
