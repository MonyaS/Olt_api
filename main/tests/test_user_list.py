import json
from rest_framework.test import APITestCase
from django.http.request import HttpRequest, QueryDict
from django.test import Client, RequestFactory
from django.http.response import JsonResponse
from rest_framework import status
from ..models import User
from ..serializers import UserSerializer
from django.urls import resolve

from ..auth import Auth
class AuthentificationTestCase(APITestCase):
    def test_login(self):
        data = {
                        "login":"admin",
                        "password":"mypassword",
                        "is_superuser":"True",
                        "can_edit":"True"
                        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        # user = User.objects.create(login=data["login"], password=data["password"], is_superuser=data["is_superuser"],can_edit=data["can_edit"])
        factory = RequestFactory()
        request = factory.post( path='/auth', data=data, content_type='application/json')
        request.method = 'LOGIN'
        responce = Auth(request)
        print(responce.content)
        print(type(responce.cookies))


        request = factory.post(path='/auth', data=data, content_type='application/json' )
        request.method = 'USER_LIST'
        request.COOKIES.update(responce.cookies)
        func,args,kwargs = resolve('/auth')
        request = func(request)
        print(request.COOKIES)
        responce = Auth(request)
        self.assertEquals(status.HTTP_200_OK,responce.status_code)
        self.assertEquals("Successfully logged in",responce.content.decode().replace('"',''))


