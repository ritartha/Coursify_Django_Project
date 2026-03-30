from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'quizzes'

router = DefaultRouter()
router.register(r'quizzes', views.QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
    # Nested questions under quiz
    path(
        'quizzes/<int:quiz_pk>/questions/',
        views.QuestionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='quiz-questions',
    ),
    path(
        'quizzes/<int:quiz_pk>/questions/<int:pk>/',
        views.QuestionViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='quiz-question-detail',
    ),
    # Nested options under question
    path(
        'quizzes/<int:quiz_pk>/questions/<int:question_pk>/options/',
        views.OptionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='question-options',
    ),
    path(
        'quizzes/<int:quiz_pk>/questions/<int:question_pk>/options/<int:pk>/',
        views.OptionViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='question-option-detail',
    ),
]
