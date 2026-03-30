from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    """Tracks student enrollment in a course."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completion_percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"

    def update_progress(self):
        """Recalculate completion percentage based on completed lessons."""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            return
        completed = self.lesson_progress.filter(is_completed=True).count()
        self.completion_percentage = round((completed / total_lessons) * 100, 1)
        self.is_completed = self.completion_percentage >= 100
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        self.save()


class LessonProgress(models.Model):
    """Tracks progress for individual lessons."""
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='progress',
    )
    is_completed = models.BooleanField(default=False)
    last_watched_position = models.PositiveIntegerField(
        default=0,
        help_text='Last watched position in seconds',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        status = '✓' if self.is_completed else f'{self.last_watched_position}s'
        return f"{self.enrollment.student.username} - {self.lesson.title} [{status}]"


class Certificate(models.Model):
    """Certificate issued upon course completion."""
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='certificate',
    )
    certificate_id = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate {self.certificate_id}"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            import uuid
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
