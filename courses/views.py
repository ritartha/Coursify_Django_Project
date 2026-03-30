from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsInstructor, IsOwnerOrReadOnly
from .models import Course, Section, Lesson, Bookmark, Wishlist
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseCreateSerializer,
    SectionSerializer, SectionCreateSerializer, LessonSerializer,
    BookmarkSerializer, WishlistSerializer,
)
from .filters import CourseFilter


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for courses.
    - List/retrieve: anyone (only published courses for non-owners)
    - Create: instructors only
    - Update/delete: course owner or admin
    """
    filterset_class = CourseFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'title']
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Course.objects.select_related('instructor').prefetch_related(
            'sections__lessons'
        )
        if self.action == 'list':
            if self.request.user.is_authenticated and self.request.user.role == 'instructor':
                # Instructors see their own (published + unpublished)
                return qs.filter(instructor=self.request.user) | qs.filter(is_published=True)
            return qs.filter(is_published=True)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return CourseCreateSerializer
        return CourseDetailSerializer

    def get_permissions(self):
        if self.action in ('create',):
            return [permissions.IsAuthenticated(), IsInstructor()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['post'], url_path='publish')
    def toggle_publish(self, request, slug=None):
        """Toggle course published status."""
        course = self.get_object()
        if course.instructor != request.user and request.user.role != 'admin':
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        course.is_published = not course.is_published
        course.save()
        return Response({
            'is_published': course.is_published,
            'detail': 'Published' if course.is_published else 'Unpublished',
        })


class SectionViewSet(viewsets.ModelViewSet):
    """CRUD for course sections."""
    serializer_class = SectionSerializer

    def get_queryset(self):
        return Section.objects.filter(
            course__slug=self.kwargs.get('course_slug')
        ).prefetch_related('lessons')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return SectionCreateSerializer
        return SectionSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        course = Course.objects.get(slug=self.kwargs['course_slug'])
        serializer.save(course=course)


class LessonViewSet(viewsets.ModelViewSet):
    """CRUD for lessons within a section."""
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(
            section__course__slug=self.kwargs.get('course_slug'),
            section_id=self.kwargs.get('section_pk'),
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        section = Section.objects.get(
            pk=self.kwargs['section_pk'],
            course__slug=self.kwargs['course_slug'],
        )
        serializer.save(section=section)


class BookmarkViewSet(viewsets.ModelViewSet):
    """Manage lesson bookmarks for the current user."""
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('lesson')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistViewSet(viewsets.ModelViewSet):
    """Manage course wishlist for the current user."""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('course')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
