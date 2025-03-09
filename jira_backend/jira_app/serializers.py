from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, Comment

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")  # Show username instead of ID

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "created_at"]

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)  # ✅ Include comments

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "priority", "assigned_to", "deadline", "comments", "updated_at", "project"]

    def get_assigned_to(self, obj):
        if obj.assigned_to:
            return {
                "id": obj.assigned_to.id,
                "username": obj.assigned_to.username,
                "email": obj.assigned_to.email,
            }
        return None


# Project Serializer
class ProjectSerializer(serializers.ModelSerializer):
    team_members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

