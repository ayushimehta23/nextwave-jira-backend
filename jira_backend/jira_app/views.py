from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Project, Task, Comment
from .serializers import ProjectSerializer, TaskSerializer, CommentSerializer, UserSerializer

# ----------------- 🔹 Authentication Views 🔹 -----------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        
        if not all([username, email, password]):
            return Response({"error": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=400)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({"message": "User created successfully"}, status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("username")  # Can be either username or email
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"error": "Both fields are required"}, status=400)

        user = authenticate(username=identifier, password=password)

        if not user:
            user = User.objects.filter(email=identifier).first()
            if user:
                user = authenticate(username=user.username, password=password)
            
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            })
        
        return Response({"error": "Invalid credentials"}, status=401)
    

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.filter(is_superuser=False).values("id", "username", "email")
        return Response(users, status=status.HTTP_200_OK)


# ----------------- 🔹 Helper Function 🔹 -----------------

def get_project_or_403(pk, user):
    """ Fetch project only if user is authorized """
    try:
        project = Project.objects.prefetch_related("team_members").get(pk=pk)
        if user not in project.team_members.all():
            return None
        return project
    except Project.DoesNotExist:
        return None

# ----------------- 🔹 Project Views 🔹 -----------------

class ProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(team_members=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()  # Save project first

            # 🔹 Add the creator as a team member
            project.team_members.add(request.user)

            # 🔹 Add additional team members from request
            team_member_ids = request.data.get("team_members", [])
            if team_member_ids:
                users = User.objects.filter(id__in=team_member_ids)
                project.team_members.add(*users)

            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        project = get_project_or_403(pk, request.user)
        if not project:
            return Response({"error": "Not authorized or project not found"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectSerializer(project)  # Now includes team_members
        return Response(serializer.data)

    def put(self, request, pk):
        project = get_project_or_403(pk, request.user)
        if not project:
            return Response({"error": "Not authorized or project not found"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = get_project_or_403(pk, request.user)
        if not project:
            return Response({"error": "Not authorized or project not found"}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response({"message": "Project deleted"}, status=status.HTTP_204_NO_CONTENT)
    
class ProjectAssignedUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        """
        Fetch all users assigned to a specific project.
        """
        project = get_object_or_404(Project, id=project_id)
        
        # Assuming there's a ManyToManyField `team_members` in the Project model
        assigned_users = project.team_members.all()

        serializer = UserSerializer(assigned_users, many=True)
        return Response(serializer.data)

# ----------------- 🔹 Task Views 🔹 -----------------

class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        """ Fetch all tasks for a project if the user is authorized """
        project = get_project_or_403(project_id, request.user)
        if not project:
            return Response({"error": "Not authorized or project not found"}, status=status.HTTP_403_FORBIDDEN)

        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        """ Create a new task under a specific project with priority """
        project = get_project_or_403(project_id, request.user)
        if not project:
            return Response({"error": "Not authorized or project not found"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data["project"] = project.id  # Explicitly link the task to the project

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            task = serializer.save(project=project)  # Save task
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        """
        Update the status and priority of a task if the user is part of the project.
        """
        task = Task.objects.filter(id=task_id, project__team_members=request.user).first()

        if not task:
            return Response({"error": "Not authorized or task not found"}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        new_priority = request.data.get("priority")

        if new_status and new_status not in ["to_do", "in_progress", "done"]:
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

        if new_priority and new_priority not in ["low", "medium", "high"]:
            return Response({"error": "Invalid priority value"}, status=status.HTTP_400_BAD_REQUEST)

        if new_status:
            task.status = new_status

        if new_priority:
            task.priority = new_priority

        task.save()

        return Response({"message": "Task updated successfully", "task": TaskSerializer(task).data})


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if request.user not in task.project.team_members.all():
                return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


# ----------------- 🔹 Comment Views 🔹 -----------------

class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = Task.objects.filter(id=task_id, project__team_members=request.user).first()
        if not task:
            return Response({"error": "Not authorized or task not found"}, status=status.HTTP_403_FORBIDDEN)
        comments = Comment.objects.filter(task=task)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = Task.objects.filter(id=task_id, project__team_members=request.user).first()
        if not task:
            return Response({"error": "Not authorized or task not found"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data["task"] = task.id
        data["user"] = request.user.id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
