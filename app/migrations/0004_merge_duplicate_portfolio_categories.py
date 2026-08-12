from django.db import migrations

# Old category names (created by hand before the canonical 6 were seeded)
# that turned out to be near-duplicates of a canonical one, because their
# exact text didn't match (singular/missing "ё") so the 0003 migration
# couldn't recognize them as the same category and created a new row.
# Maps old name -> canonical slug (from 0003) to merge into.
DUPLICATES = {
    "Решетка": "grilles",
    "Навес": "canopies",
}


def merge_duplicates(apps, schema_editor):
    PortfolioCategory = apps.get_model("app", "PortfolioCategory")
    PortfolioItem = apps.get_model("app", "PortfolioItem")

    for old_name, canonical_slug in DUPLICATES.items():
        old_category = PortfolioCategory.objects.filter(name=old_name).first()
        canonical_category = PortfolioCategory.objects.filter(
            slug=canonical_slug
        ).first()
        if not old_category or not canonical_category:
            continue
        # Move any photos filed under the old duplicate to the real one,
        # then remove the now-empty duplicate. Never touch a category that
        # still has items outside this explicit reassignment.
        PortfolioItem.objects.filter(category=old_category).update(
            category=canonical_category
        )
        old_category.delete()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_seed_portfolio_categories"),
    ]

    operations = [
        migrations.RunPython(merge_duplicates, noop_reverse),
    ]
