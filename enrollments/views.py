from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from courses.models import Course
from .models import Enrollment, LessonProgress, Certificate
from .serializers import (
    EnrollmentSerializer, EnrollSerializer,
    LessonProgressSerializer, CertificateSerializer,
)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """Manage enrollments for the current user."""
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__instructor', 'certificate')

    def create(self, request, *args, **kwargs):
        """Enroll in a course."""
        serializer = EnrollSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = Course.objects.get(id=serializer.validated_data['course_id'])

        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'detail': 'Already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course,
        )
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get lesson-by-lesson progress for an enrollment."""
        enrollment = self.get_object()
        progress = enrollment.lesson_progress.select_related('lesson').all()
        serializer = LessonProgressSerializer(progress, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def certificate(self, request, pk=None):
        """Get or generate certificate for completed course."""
        enrollment = self.get_object()
        if not enrollment.is_completed:
            return Response(
                {'detail': 'Course not yet completed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cert, created = Certificate.objects.get_or_create(enrollment=enrollment)
        return Response(CertificateSerializer(cert).data)


class LessonProgressViewSet(viewsets.ModelViewSet):
    """Track lesson progress — mark as complete, update watch position."""
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        return LessonProgress.objects.filter(
            enrollment__student=self.request.user,
        ).select_related('lesson', 'enrollment')

    def create(self, request, *args, **kwargs):
        """Create or update lesson progress."""
        lesson_id = request.data.get('lesson')
        enrollment_id = request.data.get('enrollment')
        is_completed = request.data.get('is_completed', False)
        position = request.data.get('last_watched_position', 0)

        try:
            enrollment = Enrollment.objects.get(
                id=enrollment_id, student=request.user
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': 'Enrollment not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        progress, created = LessonProgress.objects.update_or_create(
            enrollment=enrollment,
            lesson_id=lesson_id,
            defaults={
                'is_completed': is_completed,
                'last_watched_position': position,
                'completed_at': timezone.now() if is_completed else None,
            },
        )

        # Update enrollment progress
        enrollment.update_progress()

        return Response(
            LessonProgressSerializer(progress).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
