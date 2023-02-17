import json
from rest_framework.test import APITestCase
from django.http.request import HttpRequest, QueryDict
from django.test import Client
from django.http.response import JsonResponse
from rest_framework import status
from django.core.handlers.wsgi import WSGIRequest
from io import StringIO


from ..auth import Auth
class AuthentificationTestCase(APITestCase):
    def test_login(self):
        data = {
                        "login":"admin",
                        "password":"mypassword",
                        "is_superuser":"True",
                        "can_edit":"True"
                        }
        print(StringIO(str(data)))
        request = WSGIRequest({
          'REQUEST_METHOD': 'LOGIN',
          'PATH_INFO': '/auth',
          'wsgi.input': StringIO(str(data))})
        
        responce = Auth(request)
        self.assertEquals(status.HTTP_200_OK,responce.status_code)
        content = responce.content
        print(type(content))
        print("start",content,"end")
        self.assertEquals(JsonResponse("Successfully logged in", safe=False),responce)


