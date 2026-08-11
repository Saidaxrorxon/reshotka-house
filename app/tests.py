import base64
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import resolve, reverse

from .models import (
    Catalog_card,
    ConsultationRequest,
    PortfolioCategory,
    PortfolioItem,
    WorkCard,
)
from . import views

# Smallest possible valid PNG (1x1, transparent), used to give ImageFields
# real file content without needing test-fixture image files on disk.
_TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def tiny_png(name="test.png"):
    return SimpleUploadedFile(
        name, base64.b64decode(_TINY_PNG_B64), content_type="image/png"
    )


class MediaRootTestCase(TestCase):
    """Base class that redirects MEDIA_ROOT to a scratch dir for the
    duration of the test class, so uploaded test images never land in the
    real portfolio/works/catalog_cards directories."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_root = tempfile.mkdtemp(prefix="reshotka-test-media-")
        cls._override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)
        super().tearDownClass()


class PortfolioCategoryModelTests(MediaRootTestCase):
    def test_str_returns_name(self):
        category = PortfolioCategory.objects.create(name="Ворота", slug="gates")
        self.assertEqual(str(category), "Ворота")

    def test_duplicate_name_raises_integrity_error(self):
        PortfolioCategory.objects.create(name="Ворота", slug="gates")
        with self.assertRaises(IntegrityError):
            PortfolioCategory.objects.create(name="Ворота", slug="gates-2")

    def test_duplicate_slug_raises_integrity_error(self):
        PortfolioCategory.objects.create(name="Ворота", slug="gates")
        with self.assertRaises(IntegrityError):
            PortfolioCategory.objects.create(name="Другое", slug="gates")


class PortfolioItemModelTests(MediaRootTestCase):
    def setUp(self):
        self.category = PortfolioCategory.objects.create(
            name="Ворота", slug="gates"
        )

    def test_first_item_gets_uid_one(self):
        item = PortfolioItem.objects.create(
            category=self.category, image=tiny_png()
        )
        self.assertEqual(item.uid, 1)

    def test_next_item_gets_incremented_uid(self):
        PortfolioItem.objects.create(category=self.category, image=tiny_png())
        second = PortfolioItem.objects.create(
            category=self.category, image=tiny_png()
        )
        self.assertEqual(second.uid, 2)

    def test_uid_increments_from_max_existing_value(self):
        PortfolioItem.objects.create(
            category=self.category, image=tiny_png(), uid=10
        )
        next_item = PortfolioItem.objects.create(
            category=self.category, image=tiny_png()
        )
        self.assertEqual(next_item.uid, 11)

    def test_explicit_uid_is_preserved(self):
        item = PortfolioItem.objects.create(
            category=self.category, image=tiny_png(), uid=42
        )
        self.assertEqual(item.uid, 42)

    def test_str_format(self):
        item = PortfolioItem.objects.create(
            category=self.category, image=tiny_png()
        )
        self.assertEqual(str(item), f"Проект #{item.uid} ({self.category})")

    def test_default_ordering_is_by_uid(self):
        PortfolioItem.objects.create(
            category=self.category, image=tiny_png(), uid=5
        )
        PortfolioItem.objects.create(
            category=self.category, image=tiny_png(), uid=1
        )
        PortfolioItem.objects.create(
            category=self.category, image=tiny_png(), uid=3
        )
        uids = list(PortfolioItem.objects.values_list("uid", flat=True))
        self.assertEqual(uids, [1, 3, 5])


class WorkCardModelTests(MediaRootTestCase):
    def test_str_returns_title(self):
        work = WorkCard.objects.create(
            category_slug="grilles",
            image=tiny_png(),
            title="Кованая решётка",
            line_text="01 grilles",
        )
        self.assertEqual(str(work), "Кованая решётка")


class CatalogCardModelTests(MediaRootTestCase):
    def test_str_uses_category_display_and_price(self):
        card = Catalog_card.objects.create(
            image=tiny_png(), category="gates", price=500
        )
        self.assertEqual(str(card), "Ворота — 500 $")

    def test_default_category_is_railings(self):
        card = Catalog_card.objects.create(image=tiny_png(), price=100)
        self.assertEqual(card.category, "railings")

    def test_full_clean_accepts_valid_category(self):
        card = Catalog_card(image=tiny_png(), category="grilles", price=100)
        card.full_clean()  # should not raise

    def test_full_clean_rejects_invalid_category(self):
        card = Catalog_card(image=tiny_png(), category="not-a-category", price=100)
        with self.assertRaises(ValidationError):
            card.full_clean()


class ConsultationRequestModelTests(TestCase):
    def test_str_format(self):
        request = ConsultationRequest.objects.create(
            name="Иван", phone="+998901234567"
        )
        self.assertEqual(str(request), "Иван - +998901234567")

    def test_created_at_is_auto_populated(self):
        request = ConsultationRequest.objects.create(
            name="Иван", phone="+998901234567"
        )
        self.assertIsNotNone(request.created_at)


class HomeViewTests(MediaRootTestCase):
    def setUp(self):
        self.client = Client()
        self.category_b = PortfolioCategory.objects.create(
            name="Ящики", slug="boxes"
        )
        self.category_a = PortfolioCategory.objects.create(
            name="Автоворота", slug="auto-gates"
        )
        self.item = PortfolioItem.objects.create(
            category=self.category_a, image=tiny_png()
        )
        self.work_card = WorkCard.objects.create(
            category_slug="grilles",
            image=tiny_png(),
            title="Кованая решётка",
            line_text="01 grilles",
        )

    def test_get_returns_200_and_uses_index_template(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_get_context_contains_expected_objects(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(
            list(response.context["categories"]),
            [self.category_a, self.category_b],  # ordered by name
        )
        self.assertEqual(list(response.context["items"]), [self.item])
        self.assertEqual(list(response.context["work_cards"]), [self.work_card])

    def test_post_creates_consultation_request_and_redirects(self):
        response = self.client.post(
            reverse("home"),
            {"name": "Иван", "phone": "+998901234567", "message": "Хочу ворота"},
        )
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(ConsultationRequest.objects.count(), 1)
        created = ConsultationRequest.objects.get()
        self.assertEqual(created.name, "Иван")
        self.assertEqual(created.phone, "+998901234567")
        self.assertEqual(created.message, "Хочу ворота")

    def test_post_without_name_or_phone_raises_integrity_error(self):
        # Documents current behavior: the view does not validate the
        # submitted data before saving, so a POST missing "name"/"phone"
        # crashes with an IntegrityError (a 500 in production) instead of
        # being rejected gracefully. This is a known gap, not desired
        # behavior.
        with self.assertRaises(IntegrityError):
            self.client.post(reverse("home"), {})


class CatalogViewTests(MediaRootTestCase):
    def test_get_returns_200_and_uses_catalog_template(self):
        response = self.client.get(reverse("catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog.html")

    def test_context_contains_catalog_cards(self):
        card = Catalog_card.objects.create(
            image=tiny_png(), category="gates", price=500
        )
        response = self.client.get(reverse("catalog"))
        self.assertEqual(list(response.context["catalog_card"]), [card])


class ProjectsViewTests(MediaRootTestCase):
    def test_get_returns_200_and_uses_projects_template(self):
        response = self.client.get(reverse("projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_context_contains_categories_and_items(self):
        category = PortfolioCategory.objects.create(name="Ворота", slug="gates")
        item = PortfolioItem.objects.create(category=category, image=tiny_png())
        response = self.client.get(reverse("projects"))
        self.assertEqual(list(response.context["categories"]), [category])
        self.assertEqual(list(response.context["items"]), [item])


class ContactViewTests(TestCase):
    def test_get_returns_200_and_uses_contact_template(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")


class UrlResolutionTests(TestCase):
    def test_home_resolves_to_home_view(self):
        self.assertIs(resolve(reverse("home")).func, views.home)

    def test_catalog_resolves_to_catalog_view(self):
        self.assertIs(resolve(reverse("catalog")).func, views.catalog)

    def test_contact_resolves_to_contact_view(self):
        self.assertIs(resolve(reverse("contact")).func, views.contact)

    def test_projects_resolves_to_projects_view(self):
        self.assertIs(resolve(reverse("projects")).func, views.projects)


class AdminSiteTests(MediaRootTestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.client.force_login(self.superuser)

    def test_changelists_are_reachable(self):
        models = [
            PortfolioCategory,
            PortfolioItem,
            WorkCard,
            Catalog_card,
            ConsultationRequest,
        ]
        for model in models:
            url = reverse(
                f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
            )
            with self.subTest(model=model.__name__):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
