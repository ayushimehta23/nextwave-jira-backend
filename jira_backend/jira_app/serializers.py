from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, Comment

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

# Task Serializer (Move this above ProjectSerializer)
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True
    )  # Allow task assignment
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )  # Allow selecting a project

    class Meta:
        model = Task
        fields = "__all__"

# Project Serializer
class ProjectSerializer(serializers.ModelSerializer):
    team_members = UserSerializer(many=True, read_only=True)  # Nested team members
    tasks = TaskSerializer(many=True, read_only=True)  # Include related tasks

    class Meta:
        model = Project
        fields = "__all__"  # Ensure all fields are included

# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )  # Allow specifying the user
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all()
    )  # Allow specifying the task

    class Meta:
        model = Comment
        fields = "__all__"
