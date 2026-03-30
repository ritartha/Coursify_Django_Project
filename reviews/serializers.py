from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer."""
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'user_avatar', 'course',
                  'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context.get('request')
        course = attrs.get('course')

        if request and request.method == 'POST':
            # Check if already reviewed
            if Review.objects.filter(user=request.user, course=course).exists():
                raise serializers.ValidationError(
                    'You have already reviewed this course.'
                )

            # Check if enrolled
            from enrollments.models import Enrollment
            if not Enrollment.objects.filter(
                student=request.user, course=course
            ).exists():
                raise serializers.ValidationError(
                    'You must be enrolled to review this course.'
                )
        return attrs
