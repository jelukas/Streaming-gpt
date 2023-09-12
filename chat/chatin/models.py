from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField  # Si estás utilizando PostgreSQL
import uuid


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True)
    
    # Aquí está el campo JSON para la conversación completa
    conversation = JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + " - " + str(self.conversation)
