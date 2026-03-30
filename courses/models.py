from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Course(models.Model):
    """Course model — the main entity."""

    class Category(models.TextChoices):
        DEVELOPMENT = 'development', 'Development'
        BUSINESS = 'business', 'Business'
        DESIGN = 'design', 'Design'
        MARKETING = 'marketing', 'Marketing'
        MUSIC = 'music', 'Music'
        PHOTOGRAPHY = 'photography', 'Photography'
        HEALTH = 'health', 'Health & Fitness'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_created',
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_lessons(self):
        return sum(s.lessons.count() for s in self.sections.all())

    @property
    def total_duration(self):
        total = 0
        for section in self.sections.all():
            for lesson in section.lessons.all():
                total += lesson.duration or 0
        return total

    @property
    def average_rating(self):
        from reviews.models import Review
        avg = Review.objects.filter(course=self).aggregate(
            avg=models.Avg('rating')
        )['avg']
        return round(avg, 1) if avg else 0.0

    @property
    def students_count(self):
        return self.enrollments.count()


class Section(models.Model):
    """Section within a course — groups lessons together."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Individual lesson within a section."""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, default='')
    duration = models.PositiveIntegerField(help_text='Duration in seconds', default=0)
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text='Free preview lesson')
    content = models.TextField(blank=True, default='', help_text='Text content / notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    @property
    def duration_formatted(self):
        if not self.duration:
            return '0:00'
        minutes, seconds = divmod(self.duration, 60)
        return f"{minutes}:{seconds:02d}"


class Bookmark(models.Model):
    """Bookmark a lesson for later reference."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks'
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.username} → {self.lesson.title}"


class Wishlist(models.Model):
    """Wishlist a course."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} ♡ {self.course.title}"
