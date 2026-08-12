from django.db import models

class PortfolioCategory(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название категории"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Слаг категории"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class PortfolioItem(models.Model):
    category = models.ForeignKey(
        PortfolioCategory,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Категория"
    )
    image = models.ImageField(
        upload_to="portfolio/",
        verbose_name="Изображение"
    )
    uid = models.PositiveIntegerField(
        unique=True,
        editable=False,
        verbose_name="Уникальный ID"
    )

    class Meta:
        verbose_name = "Портфолио"
        verbose_name_plural = "Портфолио"
        ordering = ["uid"]

    def save(self, *args, **kwargs):
        if not self.uid:
            last_item = PortfolioItem.objects.order_by("-uid").first()
            self.uid = (last_item.uid + 1) if last_item else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Проект #{self.uid} ({self.category})"


class WorkCard(models.Model):
    """Для блока 'Наши работы'"""
    category_slug = models.SlugField(
        max_length=50,
        verbose_name="Слаг категории (например: grilles)"
    )
    image = models.ImageField(
        upload_to="works/",
        verbose_name="Изображение"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок карточки"
    )
    line_text = models.CharField(
        max_length=100,
        verbose_name="Текст в line (например: '01 grilles')"
    )

    class Meta:
        verbose_name = "Карточка работы"
        verbose_name_plural = "Карточки работ"

    def __str__(self):
        return self.title



class Catalog_card(models.Model):
    CATEGORY_CHOICES = [
        ('railings', 'Перила'),
        ('canopies', 'Навесы'),
        ('gates', 'Ворота'),
        ('grilles', 'Решётка')
    ]
    image = models.ImageField(upload_to="catalog_cards/", verbose_name="Изображение")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='railings',  # например, "Перила"
        verbose_name="Категория"
    )
    price = models.PositiveIntegerField(verbose_name="Цена")

    def __str__(self):
        return f"{self.get_category_display()} — {self.price} $"
    
    
    
    
    
    
    


class ConsultationRequest(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    message = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name = "Заявка на консультацию"
        verbose_name_plural = "Заявки на консультацию"


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    name = models.CharField(max_length=100, verbose_name="Имя")
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, default=5, verbose_name="Оценка"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.rating}/5"

    @property
    def star_display(self):
        return "★" * self.rating + "☆" * (5 - self.rating)