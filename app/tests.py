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
    Review,
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
        category = PortfolioCategory.objects.create(name="Тестовая", slug="test-cat")
        self.assertEqual(str(category), "Тестовая")

    def test_duplicate_name_raises_integrity_error(self):
        PortfolioCategory.objects.create(name="Тестовая", slug="test-cat")
        with self.assertRaises(IntegrityError):
            PortfolioCategory.objects.create(name="Тестовая", slug="test-cat-2")

    def test_duplicate_slug_raises_integrity_error(self):
        PortfolioCategory.objects.create(name="Тестовая", slug="test-cat")
        with self.assertRaises(IntegrityError):
            PortfolioCategory.objects.create(name="Другое", slug="test-cat")

    def test_migration_seeds_the_six_real_categories(self):
        expected = {
            "Решётки": "grilles",
            "Перила": "railings",
            "Навесы": "canopies",
            "Ворота": "gates",
            "Заборы": "fences",
            "Каркасные ангары": "hangars",
        }
        actual = dict(
            PortfolioCategory.objects.filter(name__in=expected).values_list(
                "name", "slug"
            )
        )
        self.assertEqual(actual, expected)


class PortfolioItemModelTests(MediaRootTestCase):
    def setUp(self):
        self.category = PortfolioCategory.objects.create(
            name="Тестовая", slug="test-cat"
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


class ReviewModelTests(TestCase):
    def test_str_format(self):
        review = Review.objects.create(name="Иван", rating=4, text="Отлично")
        self.assertEqual(str(review), "Иван — 4/5")

    def test_defaults_to_unapproved(self):
        review = Review.objects.create(name="Иван", text="Отлично")
        self.assertFalse(review.is_approved)

    def test_default_ordering_is_newest_first(self):
        older = Review.objects.create(name="Первый", text="А")
        newer = Review.objects.create(name="Второй", text="Б")
        self.assertEqual(list(Review.objects.all()), [newer, older])

    def test_star_display(self):
        review = Review.objects.create(name="Иван", rating=3, text="Норм")
        self.assertEqual(review.star_display, "★★★☆☆")


class HomeViewTests(MediaRootTestCase):
    def setUp(self):
        self.client = Client()

    def test_get_returns_200_and_uses_index_template(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_hero_slides_built_from_latest_portfolio_items(self):
        category = PortfolioCategory.objects.get(slug="grilles")
        item = PortfolioItem.objects.create(category=category, image=tiny_png())
        response = self.client.get(reverse("home"))
        slides = response.context["hero_slides"]
        self.assertEqual(len(slides), 1)
        self.assertEqual(slides[0]["title"], "Решётки")
        self.assertEqual(slides[0]["image"], views.CATEGORY_HERO_IMAGES["grilles"])
        self.assertIn(b'"hero-slides-data"', response.content)

    def test_hero_slides_empty_when_no_portfolio_items(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["hero_slides"], [])

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

    def test_post_without_name_or_phone_does_not_create_record(self):
        response = self.client.post(reverse("home"), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConsultationRequest.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)

    def test_post_without_name_or_phone_shows_field_errors(self):
        response = self.client.post(reverse("home"), {})
        self.assertContains(response, "Пожалуйста, укажите имя.")
        self.assertContains(response, "Пожалуйста, укажите телефон.")

    def test_post_with_whitespace_only_name_does_not_create_record(self):
        response = self.client.post(
            reverse("home"), {"name": "   ", "phone": "+998901234567"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConsultationRequest.objects.count(), 0)

    def test_context_only_contains_approved_reviews(self):
        approved = Review.objects.create(
            name="Иван", text="Отлично", is_approved=True
        )
        Review.objects.create(name="Скрытый", text="Не одобрен", is_approved=False)
        response = self.client.get(reverse("home"))
        self.assertEqual(list(response.context["reviews"]), [approved])

    def test_post_review_creates_unapproved_review_and_redirects(self):
        response = self.client.post(
            reverse("home"),
            {"form_type": "review", "name": "Иван", "rating": "4", "text": "Класс"},
        )
        self.assertRedirects(
            response, f"{reverse('home')}?review=sent#reviews",
            fetch_redirect_response=False,
        )
        self.assertEqual(Review.objects.count(), 1)
        created = Review.objects.get()
        self.assertEqual(created.name, "Иван")
        self.assertEqual(created.rating, 4)
        self.assertFalse(created.is_approved)

    def test_post_review_without_name_or_text_does_not_create_record(self):
        response = self.client.post(reverse("home"), {"form_type": "review"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)
        self.assertTrue(response.context["review_form"].errors)

    def test_post_review_does_not_affect_consultation_form(self):
        self.client.post(
            reverse("home"),
            {"form_type": "review", "name": "Иван", "rating": "4", "text": "Класс"},
        )
        self.assertEqual(ConsultationRequest.objects.count(), 0)


class ProjectsViewTests(MediaRootTestCase):
    def test_get_returns_200_and_uses_projects_template(self):
        response = self.client.get(reverse("projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_context_contains_categories_and_items(self):
        # The 6 real categories are seeded by a data migration - reuse one
        # rather than creating a duplicate.
        category = PortfolioCategory.objects.get(slug="gates")
        item = PortfolioItem.objects.create(category=category, image=tiny_png())
        response = self.client.get(reverse("projects"))
        self.assertIn(category, response.context["categories"])
        self.assertEqual(list(response.context["items"]), [item])


class ContactViewTests(TestCase):
    def test_get_returns_200_and_uses_contact_template(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")


class SeoViewTests(TestCase):
    def test_robots_txt_returns_200_and_references_sitemap(self):
        response = self.client.get(reverse("robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn(b"Sitemap: ", response.content)
        self.assertIn(b"/sitemap.xml", response.content)

    def test_sitemap_xml_returns_200_and_lists_all_pages(self):
        response = self.client.get(reverse("sitemap_xml"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        for name in ("home", "projects", "contact"):
            self.assertIn(reverse(name).encode(), response.content)


class UrlResolutionTests(TestCase):
    def test_home_resolves_to_home_view(self):
        self.assertIs(resolve(reverse("home")).func, views.home)

    def test_contact_resolves_to_contact_view(self):
        self.assertIs(resolve(reverse("contact")).func, views.contact)

    def test_projects_resolves_to_projects_view(self):
        self.assertIs(resolve(reverse("projects")).func, views.projects)

    def test_robots_txt_resolves_to_robots_txt_view(self):
        self.assertIs(resolve(reverse("robots_txt")).func, views.robots_txt)

    def test_sitemap_xml_resolves_to_sitemap_xml_view(self):
        self.assertIs(resolve(reverse("sitemap_xml")).func, views.sitemap_xml)


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
            Review,
        ]
        for model in models:
            url = reverse(
                f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
            )
            with self.subTest(model=model.__name__):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
