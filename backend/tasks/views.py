from datetime import date, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task
from .serializers import (
    AnalyzeRequestSerializer,
    ScoredTaskSerializer,
    TaskModelSerializer,
)
from .scoring import score_tasks, CircularDependencyError, DEFAULT_STRATEGY


class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/
    Body:
    {
      "strategy": "smart_balance" | "fastest_wins" | "high_impact" | "deadline_driven",
      "tasks": [
        {
          "id": "1",
          "title": "...",
          "due_date": "2025-01-01",
          "estimated_hours": 3.5,
          "importance": 8,
          "dependencies": ["2", "3"]
        },
        ...
      ]
    }
    """

    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response(
                {"detail": "Request body cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyzeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        strategy = data.get("strategy", DEFAULT_STRATEGY)
        tasks_data = data["tasks"]

        # Convert validated data into plain dicts for scoring
        # due_date is already a date object
        try:
            raw_tasks = []
            for t in tasks_data:
                raw_tasks.append(
                    {
                        "id": t.get("id"),
                        "title": t["title"],
                        "due_date": t["due_date"],
                        "estimated_hours": t["estimated_hours"],
                        "importance": t["importance"],
                        "dependencies": t.get("dependencies") or [],
                    }
                )

            scored_tasks = score_tasks(raw_tasks, strategy=strategy)

        except CircularDependencyError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serialize output
        output = [st.data for st in scored_tasks]
        out_serializer = ScoredTaskSerializer(output, many=True)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/?strategy=smart_balance

    Uses Task instances stored in the DB and returns the top 3 tasks
    to work on "today" based on the strategy.
    """

    def get(self, request, *args, **kwargs):
        strategy = request.query_params.get("strategy", DEFAULT_STRATEGY)

        today = date.today()
        # Consider overdue + next 7 days as "today context"
        cutoff = today + timedelta(days=7)

        queryset = Task.objects.filter(due_date__lte=cutoff).order_by("due_date")

        if not queryset.exists():
            return Response(
                {"detail": "No tasks available to suggest."},
                status=status.HTTP_200_OK,
            )

        model_serializer = TaskModelSerializer(queryset, many=True)
        tasks_data = model_serializer.data

        # Convert to plain dicts suitable for scoring
        raw_tasks = []
        for t in tasks_data:
            raw_tasks.append(
                {
                    "id": str(t["id"]),
                    "title": t["title"],
                    "due_date": t["due_date"],
                    "estimated_hours": t["estimated_hours"],
                    "importance": t["importance"],
                    "dependencies": [str(d_id) for d_id in t.get("dependencies", [])],
                }
            )

        # Convert due_date strings back to date objects for scoring
        from datetime import datetime

        for t in raw_tasks:
            if isinstance(t["due_date"], str):
                t["due_date"] = datetime.strptime(t["due_date"], "%Y-%m-%d").date()

        try:
            scored_tasks = score_tasks(raw_tasks, strategy=strategy)
        except CircularDependencyError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        top_three = [st.data for st in scored_tasks[:3]]
        out_serializer = ScoredTaskSerializer(top_three, many=True)
        return Response(out_serializer.data, status=status.HTTP_200_OK)
