from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'courses'

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'bookmarks', views.BookmarkViewSet, basename='bookmark')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
    # Nested sections under course
    path(
        'courses/<slug:course_slug>/sections/',
        views.SectionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='course-sections',
    ),
    path(
        'courses/<slug:course_slug>/sections/<int:pk>/',
        views.SectionViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='course-section-detail',
    ),
    # Nested lessons under section
    path(
        'courses/<slug:course_slug>/sections/<int:section_pk>/lessons/',
        views.LessonViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='section-lessons',
    ),
    path(
        'courses/<slug:course_slug>/sections/<int:section_pk>/lessons/<int:pk>/',
        views.LessonViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='section-lesson-detail',
    ),
]
