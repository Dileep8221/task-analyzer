from datetime import date, timedelta
from django.test import TestCase

from .scoring import score_tasks, CircularDependencyError


class TestScoringAlgorithm(TestCase):

    def test_urgency_vs_importance_tradeoff(self):
        """Urgent medium-importance task should outrank far-due high-importance task."""
        today = date.today()

        tasks = [
            {
                "id": "urgent_medium",
                "title": "Pay electricity bill",
                "due_date": today + timedelta(days=1),
                "estimated_hours": 1.0,
                "importance": 7,
                "dependencies": [],
            },
            {
                "id": "far_high",
                "title": "Long-term strategy doc",
                "due_date": today + timedelta(days=20),
                "estimated_hours": 2.0,
                "importance": 9,
                "dependencies": [],
            },
        ]

        scored = score_tasks(tasks, strategy="smart_balance", today=today)
        self.assertEqual(scored[0].data["id"], "urgent_medium")

    def test_dependency_boost(self):
        """A task that unblocks multiple tasks should rank highest."""
        today = date.today()
        due = today + timedelta(days=3)

        tasks = [
            {
                "id": "A",
                "title": "Set up project",
                "due_date": due,
                "estimated_hours": 2.0,
                "importance": 7,
                "dependencies": [],
            },
            {
                "id": "B",
                "title": "Build feature",
                "due_date": due,
                "estimated_hours": 3.0,
                "importance": 7,
                "dependencies": ["A"],
            },
            {
                "id": "C",
                "title": "Write tests",
                "due_date": due,
                "estimated_hours": 3.0,
                "importance": 7,
                "dependencies": ["A"],
            },
        ]

        scored = score_tasks(tasks, strategy="smart_balance", today=today)
        self.assertEqual(scored[0].data["id"], "A")

    def test_circular_dependencies(self):
        """Circular dependency A->B->A should raise CircularDependencyError."""
        today = date.today()
        due = today + timedelta(days=5)

        tasks = [
            {
                "id": "A",
                "title": "Task A",
                "due_date": due,
                "estimated_hours": 1.0,
                "importance": 5,
                "dependencies": ["B"],
            },
            {
                "id": "B",
                "title": "Task B",
                "due_date": due,
                "estimated_hours": 1.0,
                "importance": 5,
                "dependencies": ["A"],
            },
        ]

        with self.assertRaises(CircularDependencyError):
            score_tasks(tasks, strategy="smart_balance", today=today)
