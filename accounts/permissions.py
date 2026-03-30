from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """Allow access only to students."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsInstructor(permissions.BasePermission):
    """Allow access only to instructors."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'instructor'


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsInstructorOrAdmin(permissions.BasePermission):
    """Allow access to instructors and admins."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('instructor', 'admin')


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: only the owner can edit."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check for 'user', 'instructor', or 'author' attribute
        for attr in ('user', 'instructor', 'author'):
            if hasattr(obj, attr):
                return getattr(obj, attr) == request.user
        return False


class IsEnrolledOrInstructor(permissions.BasePermission):
    """Allow access if user is enrolled in the course or is the instructor."""
    def has_object_permission(self, request, view, obj):
        from enrollments.models import Enrollment
        course = getattr(obj, 'course', obj)
        if hasattr(course, 'instructor') and course.instructor == request.user:
            return True
        return Enrollment.objects.filter(
            student=request.user,
            course=course,
        ).exists()
