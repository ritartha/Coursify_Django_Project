"""
Coursify URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('enrollments.urls')),
    path('api/', include('quizzes.urls')),
    path('api/', include('reviews.urls')),

    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),

    # Frontend pages
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='auth/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='auth/register.html'), name='register'),
    path('courses/', TemplateView.as_view(template_name='courses/catalog.html'), name='catalog'),
    path('courses/<slug:slug>/', TemplateView.as_view(template_name='courses/detail.html'), name='course_detail'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard/student.html'), name='student_dashboard'),
    path('instructor/', TemplateView.as_view(template_name='dashboard/instructor.html'), name='instructor_dashboard'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
