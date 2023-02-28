import secrets
from datetime import datetime

import jwt
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from OLT.settings import SECRET_KEY
from django.contrib.auth.hashers import make_password

class User(AbstractBaseUser):
    login = models.CharField(max_length=20, unique=True, null=True, blank=False)
    password = models.CharField(max_length=50)
    is_superuser = models.BooleanField(default=0)
    can_edit = models.BooleanField(default=0)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        token = jwt.encode({
            'salt': secrets.token_urlsafe(32),
            'creation_date': datetime.today().strftime("%x"),
            'login': self.login,
            'password': self.password
        }, SECRET_KEY, algorithm='HS256')
        return token

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password


# 255.255.255.255:65536
class Olt(models.Model):
    ip = models.GenericIPAddressField(unique=True, null=False, blank=False)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    olt_configuration = models.JSONField()

    # USERNAME_FIELD = 'ip'
    # REQUIRED_FIELDS = []
