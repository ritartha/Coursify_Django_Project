from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'enrollments'

router = DefaultRouter()
router.register(r'enrollments', views.EnrollmentViewSet, basename='enrollment')
router.register(r'lesson-progress', views.LessonProgressViewSet, basename='lesson-progress')

urlpatterns = [
    path('', include(router.urls)),
]
