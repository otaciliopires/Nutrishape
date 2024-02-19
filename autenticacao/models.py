from django.db import models
from django.contrib.auth.models import  AbstractUser, User
from django.utils.safestring import mark_safe



class Ativacao(models.Model):
    token = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username