from rest_framework import serializers
from .models import Course, Section, Lesson, Bookmark, Wishlist


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for lessons."""
    duration_formatted = serializers.ReadOnlyField()

    class Meta:
        model = Lesson
        fields = ['id', 'section', 'title', 'video_url', 'duration',
                  'duration_formatted', 'order', 'is_preview', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight lesson serializer for lists (hides video URL for non-preview)."""
    duration_formatted = serializers.ReadOnlyField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'duration', 'duration_formatted',
                  'order', 'is_preview']


class SectionSerializer(serializers.ModelSerializer):
    """Section serializer with nested lessons."""
    lessons = LessonListSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'course', 'title', 'order', 'lessons', 'lesson_count']
        read_only_fields = ['id']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class SectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating sections."""
    class Meta:
        model = Section
        fields = ['id', 'course', 'title', 'order']
        read_only_fields = ['id']


class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight course serializer for list views."""
    instructor_name = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()
    total_lessons = serializers.ReadOnlyField()
    students_count = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'instructor',
                  'instructor_name', 'price', 'thumbnail', 'category',
                  'is_published', 'average_rating', 'total_lessons',
                  'students_count', 'created_at']

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.username


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course serializer with nested sections and lessons."""
    instructor_name = serializers.SerializerMethodField()
    sections = SectionSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_lessons = serializers.ReadOnlyField()
    total_duration = serializers.ReadOnlyField()
    students_count = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'instructor',
                  'instructor_name', 'price', 'thumbnail', 'category',
                  'is_published', 'average_rating', 'total_lessons',
                  'total_duration', 'students_count', 'sections',
                  'created_at', 'updated_at']

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.username


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating / updating courses."""
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'thumbnail',
                  'category', 'is_published']
        read_only_fields = ['id']


class BookmarkSerializer(serializers.ModelSerializer):
    """Bookmark serializer."""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'lesson', 'lesson_title', 'created_at']
        read_only_fields = ['id', 'created_at']


class WishlistSerializer(serializers.ModelSerializer):
    """Wishlist serializer."""
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'course', 'course_title', 'created_at']
        read_only_fields = ['id', 'created_at']
