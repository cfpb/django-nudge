from django.contrib import admin
from models import Post
from nudge.admin import NudgeAdmin


admin.site.register(Post, NudgeAdmin)
