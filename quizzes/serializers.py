from rest_framework import serializers
from .models import Quiz, Question, Option, QuizAttempt, UserAnswer


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']


class OptionStudentSerializer(serializers.ModelSerializer):
    """Hides is_correct for students taking the quiz."""
    class Meta:
        model = Option
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'order', 'explanation', 'options']
        read_only_fields = ['id']


class QuestionStudentSerializer(serializers.ModelSerializer):
    """Hides explanation and correct answers for students."""
    options = OptionStudentSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'options']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'title', 'description', 'passing_score',
                  'question_count', 'questions', 'created_at']
        read_only_fields = ['id', 'created_at']


class QuizStudentSerializer(serializers.ModelSerializer):
    """Quiz view for students — hides correct answers."""
    questions = QuestionStudentSerializer(many=True, read_only=True)
    question_count = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'passing_score',
                  'question_count', 'questions']


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['question', 'selected_option']


class QuizSubmitSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers."""
    answers = UserAnswerSerializer(many=True)


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'score', 'passed',
                  'completed_at', 'answers']

    def get_answers(self, obj):
        return [{
            'question': a.question.text,
            'selected': a.selected_option.text,
            'is_correct': a.is_correct,
            'correct_answer': a.question.options.filter(is_correct=True).first().text if a.question.options.filter(is_correct=True).exists() else None,
        } for a in obj.answers.select_related('question', 'selected_option').all()]
