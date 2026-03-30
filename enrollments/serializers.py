from rest_framework import serializers
from .models import Enrollment, LessonProgress, Certificate


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for lesson progress tracking."""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'enrollment', 'lesson', 'lesson_title',
                  'is_completed', 'last_watched_position', 'completed_at', 'updated_at']
        read_only_fields = ['id', 'completed_at', 'updated_at']


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for course certificates."""
    course_title = serializers.CharField(source='enrollment.course.title', read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'certificate_id', 'course_title', 'student_name', 'issued_at']

    def get_student_name(self, obj):
        user = obj.enrollment.student
        return user.get_full_name() or user.username


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollments."""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    course_thumbnail = serializers.ImageField(source='course.thumbnail', read_only=True)
    instructor_name = serializers.SerializerMethodField()
    certificate = CertificateSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_title', 'course_slug',
                  'course_thumbnail', 'instructor_name', 'enrolled_at',
                  'completion_percentage', 'is_completed', 'completed_at', 'certificate']
        read_only_fields = ['id', 'student', 'enrolled_at', 'completion_percentage',
                           'is_completed', 'completed_at']

    def get_instructor_name(self, obj):
        return obj.course.instructor.get_full_name() or obj.course.instructor.username


class EnrollSerializer(serializers.Serializer):
    """Serializer for enrolling in a course."""
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        from courses.models import Course
        try:
            course = Course.objects.get(id=value, is_published=True)
        except Course.DoesNotExist:
            raise serializers.ValidationError('Course not found or not published.')
        return value
