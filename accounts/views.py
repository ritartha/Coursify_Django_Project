from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Count, Avg
from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UserUpdateSerializer, ChangePasswordSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Register a new user and return JWT tokens."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Login and return JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    """View and update the authenticated user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change password for authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password changed successfully.'})


class StudentDashboardView(APIView):
    """Dashboard data for students."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from enrollments.models import Enrollment
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        enrolled = enrollments.count()
        completed = enrollments.filter(completion_percentage=100).count()
        in_progress = enrolled - completed
        avg_progress = enrollments.aggregate(avg=Avg('completion_percentage'))['avg'] or 0.0

        recent_enrollments = enrollments.order_by('-enrolled_at')[:5]
        courses_data = []
        for e in recent_enrollments:
            courses_data.append({
                'id': e.course.id,
                'title': e.course.title,
                'slug': e.course.slug,
                'thumbnail': e.course.thumbnail.url if e.course.thumbnail else None,
                'progress': e.completion_percentage,
                'enrolled_at': e.enrolled_at,
            })

        return Response({
            'total_enrolled': enrolled,
            'completed': completed,
            'in_progress': in_progress,
            'average_progress': round(avg_progress, 1),
            'recent_courses': courses_data,
        })


class InstructorDashboardView(APIView):
    """Dashboard data for instructors."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from courses.models import Course
        from enrollments.models import Enrollment
        from reviews.models import Review

        courses = Course.objects.filter(instructor=request.user)
        course_ids = courses.values_list('id', flat=True)

        total_students = Enrollment.objects.filter(
            course_id__in=course_ids
        ).values('student').distinct().count()

        total_revenue = courses.aggregate(
            revenue=Sum('price')
        )['revenue'] or 0

        avg_rating = Review.objects.filter(
            course_id__in=course_ids
        ).aggregate(avg=Avg('rating'))['avg'] or 0.0

        courses_data = []
        for c in courses[:10]:
            student_count = c.enrollments.count()
            course_rating = c.reviews.aggregate(avg=Avg('rating'))['avg'] or 0.0
            courses_data.append({
                'id': c.id,
                'title': c.title,
                'slug': c.slug,
                'students': student_count,
                'rating': round(course_rating, 1),
                'revenue': float(c.price * student_count),
                'is_published': c.is_published,
            })

        return Response({
            'total_courses': courses.count(),
            'total_students': total_students,
            'total_revenue': float(total_revenue),
            'average_rating': round(avg_rating, 1),
            'courses': courses_data,
        })
