from django.contrib import admin
from jira_app.models import Project, Task, Comment  # Use absolute import

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Comment)

