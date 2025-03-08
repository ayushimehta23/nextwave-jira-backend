from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, Comment

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

# Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)  # ✅ Return full user details
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="assigned_to", write_only=True, allow_null=True
    )

    class Meta:
        model = Task
        fields = "__all__"


# Project Serializer
class ProjectSerializer(serializers.ModelSerializer):
    team_members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())

    class Meta:
        model = Comment
        fields = "__all__"
