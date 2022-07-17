from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True)
    avatar = models.ImageField(upload_to='profile/', default='profile/default.png')
    birthday = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return self.username
