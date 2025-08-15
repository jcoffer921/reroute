# core/models.py

from django.db import models
from core.constants import RELATABLE_SKILLS
from django.contrib.auth.models import User  #


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SuggestedSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
