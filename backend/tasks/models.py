from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.FloatField()
    importance = models.IntegerField()

    # This task depends on other tasks
    dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='dependents',
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.title} (importance={self.importance})"
