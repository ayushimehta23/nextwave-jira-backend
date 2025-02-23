from django.urls import path
from .views import (
    RegisterView, LoginView, UserListView,
    ProjectListCreateView, ProjectDetailView, ProjectAssignedUsersView,
    TaskListCreateView, TaskDetailView, UpdateTaskStatusView,
    CommentListCreateView
)

urlpatterns = [
    # 🔹 Authentication Endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="user-list"),

    # 🔹 Project Endpoints
    path("projects/", ProjectListCreateView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/<int:project_id>/assigned-users/", ProjectAssignedUsersView.as_view(), name="project-assigned-users"),

    # 🔹 Task Endpoints
    path("projects/<int:project_id>/tasks/", TaskListCreateView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:task_id>/update-status/", UpdateTaskStatusView.as_view(), name="update-task-status"),

    # 🔹 Comment Endpoints
    path("tasks/<int:task_id>/comments/", CommentListCreateView.as_view(), name="comment-list"),
]
