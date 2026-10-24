from rest_framework import serializers
from django.utils import timezone

from .models import Habit, HabitCompletion


class HabitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habit
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "owner",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "owner",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Habit name cannot be empty."
            )

        return value


class HabitCompletionSerializer(serializers.ModelSerializer):

    habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.none()
    )

    class Meta:
        model = HabitCompletion
        fields = [
            "id",
            "habit",
            "completed_date",
        ]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            self.fields["habit"].queryset = (
                Habit.objects.filter(owner=request.user)
            )

    def validate_completed_date(self, value):

        if value > timezone.localdate():
            raise serializers.ValidationError(
                "Completion date cannot be in the future."
            )

        return value

    def validate(self, attrs):

        habit = attrs.get(
            "habit",
            getattr(self.instance, "habit", None)
        )

        completed_date = attrs.get(
            "completed_date",
            getattr(self.instance, "completed_date", None)
        )

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        if habit and habit.owner_id != request.user.pk:
            raise serializers.ValidationError({
                "habit": "You do not own this habit."
            })

        if habit and completed_date:

            existing = HabitCompletion.objects.filter(
                habit=habit,
                completed_date=completed_date
            )

            if self.instance:
                existing = existing.exclude(
                    pk=self.instance.pk
                )

            if existing.exists():
                raise serializers.ValidationError({
                    "completed_date":
                    "This habit is already completed for this date."
                })

        return attrs