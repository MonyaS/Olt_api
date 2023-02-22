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

        new_data = {    
                        "id":2,
                        "login":"admin",
                        "password":"mypassword2",
                        "is_superuser":"True",
                        "can_edit":"True"
                        }

        new_request = factory.post(path='/auth', data=new_data, content_type='application/json' )
        new_request.method = 'DELETE_USER'
        for key, value in response.cookies.items():
            new_request.COOKIES[key] = value.value
        response = Auth(new_request)
        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Successfully delete.",response.content.decode().replace('"',''))


