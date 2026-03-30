from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsInstructor
from .models import Quiz, Question, Option, QuizAttempt, UserAnswer
from .serializers import (
    QuizSerializer, QuizStudentSerializer, QuestionSerializer,
    OptionSerializer, QuizSubmitSerializer, QuizAttemptSerializer,
)


class QuizViewSet(viewsets.ModelViewSet):
    """CRUD for quizzes — instructors manage, students view."""
    queryset = Quiz.objects.prefetch_related('questions__options').all()

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.role == 'instructor':
            return QuizSerializer
        return QuizStudentSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_quiz(self, request, pk=None):
        """Submit quiz answers and get graded results."""
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers_data = serializer.validated_data['answers']

        # Create attempt
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)

        correct = 0
        total = quiz.questions.count()

        for answer in answers_data:
            user_answer = UserAnswer.objects.create(
                attempt=attempt,
                question=answer['question'],
                selected_option=answer['selected_option'],
            )
            if user_answer.is_correct:
                correct += 1

        # Calculate score
        score = (correct / total * 100) if total > 0 else 0
        attempt.score = round(score, 1)
        attempt.passed = score >= quiz.passing_score
        attempt.save()

        return Response(QuizAttemptSerializer(attempt).data)

    @action(detail=True, methods=['get'], url_path='attempts')
    def my_attempts(self, request, pk=None):
        """Get current user's attempts for this quiz."""
        quiz = self.get_object()
        attempts = QuizAttempt.objects.filter(
            user=request.user, quiz=quiz
        ).prefetch_related('answers__question', 'answers__selected_option')
        return Response(QuizAttemptSerializer(attempts, many=True).data)


class QuestionViewSet(viewsets.ModelViewSet):
    """CRUD for quiz questions."""
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_pk')
        return Question.objects.filter(quiz_id=quiz_id).prefetch_related('options')

    def perform_create(self, serializer):
        serializer.save(quiz_id=self.kwargs['quiz_pk'])


class OptionViewSet(viewsets.ModelViewSet):
    """CRUD for question options."""
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def get_queryset(self):
        return Option.objects.filter(question_id=self.kwargs.get('question_pk'))

    def perform_create(self, serializer):
        serializer.save(question_id=self.kwargs['question_pk'])
