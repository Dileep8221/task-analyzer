from rest_framework import serializers
from .models import Task


class TaskInputSerializer(serializers.Serializer):
    """
    Serializer for tasks coming in the /api/tasks/analyze/ endpoint.
    These tasks are *not* required to be saved to the DB.
    """
    id = serializers.CharField(required=False)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField(min_value=0)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )


class AnalyzeRequestSerializer(serializers.Serializer):
    strategy = serializers.ChoiceField(
        choices=[
            'smart_balance',
            'fastest_wins',
            'high_impact',
            'deadline_driven',
        ],
        required=False,
        default='smart_balance',
    )
    tasks = TaskInputSerializer(many=True)


class ScoredTaskSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    score = serializers.FloatField()
    explanation = serializers.CharField()


class TaskModelSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model used by /api/tasks/suggest/.
    """
    dependencies = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies']
