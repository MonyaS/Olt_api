from rest_framework.test import APITestCase
from django.test import RequestFactory
from rest_framework import status
from ..serializers import UserSerializer

from ..auth import Auth

class AuthentificationTestCase(APITestCase):
    def test_login(self):
        data = {
                        "login":"admin",
                        "password":"mypassword",
                        "is_superuser":"True",
                        "can_edit":"True"
                        }
        factory = RequestFactory()
        request = factory.post( path='/auth', data=data, content_type='application/json')
        request.method = 'LOGIN'
        response = Auth(request)

        new_request = factory.post(path='/auth', data=data, content_type='application/json' )
        new_request.method = 'USER_LIST'
        for key, value in response.cookies.items():
            new_request.COOKIES[key] = value.value
        response = Auth(new_request)
        print(response.content)
        self.assertEquals(status.HTTP_200_OK,response.status_code)


