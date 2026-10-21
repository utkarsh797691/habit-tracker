from django.db import models
from django.conf import settings

class Habit(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="habit")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit,on_delete=models.CASCADE,related_name="completions")
    completed_date = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return f"{self.habit.name} - {self.completed_date}"