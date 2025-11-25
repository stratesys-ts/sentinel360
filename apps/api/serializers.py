from rest_framework import serializers
from apps.projects.models import Project, Task
from apps.timesheet.models import TimeEntry, Timesheet, Activity


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "budget",
            "external_access",
            "industry",
            "geography",
            "created_at",
            "updated_at",
        ]


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assigned_to = serializers.SerializerMethodField()
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    def get_assigned_to(self, obj):
        user = obj.assigned_to
        if not user:
            return None
        return {"id": user.id, "username": user.username, "email": user.email}

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "start_date",
            "due_date",
            "assigned_to",
            "assigned_to_id",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        user_id = validated_data.pop("assigned_to_id", None)
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(id=user_id).first()
            if user:
                validated_data["assigned_to"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_id = validated_data.pop("assigned_to_id", None)
        if user_id is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(id=user_id).first()
            instance.assigned_to = user
        return super().update(instance, validated_data)


class TimeEntrySerializer(serializers.ModelSerializer):
    project = serializers.SerializerMethodField(read_only=True)
    task = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    timesheet_id = serializers.IntegerField(write_only=True, required=True)
    project_id = serializers.IntegerField(write_only=True, required=True)
    task_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    activity_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "project",
            "task",
            "activity_id",
            "timesheet_id",
            "project_id",
            "task_id",
            "date",
            "hours",
            "description",
            "user",
        ]

    def get_project(self, obj):
        return obj.project_id

    def get_task(self, obj):
        return obj.task_id

    def get_user(self, obj):
        ts = getattr(obj, "timesheet", None)
        if ts and ts.user:
            return {"id": ts.user.id, "username": ts.user.username, "email": ts.user.email}
        return None

    def validate(self, attrs):
        # Validate foreign keys
        ts_id = attrs.get("timesheet_id")
        pr_id = attrs.get("project_id")
        task_id = attrs.get("task_id")
        act_id = attrs.get("activity_id")

        try:
            attrs["timesheet"] = Timesheet.objects.get(id=ts_id)
        except Timesheet.DoesNotExist:
            raise serializers.ValidationError({"timesheet_id": "Timesheet não encontrado."})

        try:
            attrs["project"] = Project.objects.get(id=pr_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError({"project_id": "Projeto não encontrado."})

        if task_id:
            try:
                attrs["task"] = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                raise serializers.ValidationError({"task_id": "Tarefa não encontrada."})

        if act_id:
            try:
                attrs["activity"] = Activity.objects.get(id=act_id)
            except Activity.DoesNotExist:
                raise serializers.ValidationError({"activity_id": "Atividade não encontrada."})

        return attrs

    def create(self, validated_data):
        for key in ["timesheet_id", "project_id", "task_id", "activity_id"]:
            validated_data.pop(key, None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for key in ["timesheet_id", "project_id", "task_id", "activity_id"]:
            validated_data.pop(key, None)
        return super().update(instance, validated_data)
