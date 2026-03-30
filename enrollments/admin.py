from django.contrib import admin
from .models import Enrollment, LessonProgress, Certificate


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'completion_percentage', 'is_completed', 'enrolled_at']
    list_filter = ['is_completed']
    search_fields = ['student__username', 'course__title']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'last_watched_position']
    list_filter = ['is_completed']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'enrollment', 'issued_at']
    search_fields = ['certificate_id']
