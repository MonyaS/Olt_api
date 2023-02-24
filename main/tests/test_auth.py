from datetime import date, datetime, timedelta
import secrets
from django.test import RequestFactory, TestCase
import jwt
from OLT.settings import SECRET_KEY

from main.auth import Auth

from ..models import User
from ..serializers import UserSerializer
from rest_framework import status



class UserSerializerTestCase(TestCase):
    factory = RequestFactory()
    admin_data = {
            "login":"admin",
            "password":"mypassword",
            "is_superuser":"True",
            "can_edit":"True"
            }
    @classmethod
    def setUpTestData(cls):
        # Create some data to be used by the tests
        # admin_data нужно будет поправить
        admin_data = {
            "login":"admin",
            "password":"mypassword",
            "is_superuser":"True",
            "can_edit":"True"
            }
        admin = UserSerializer(data=admin_data)
        if admin.is_valid():
            admin.save()
        
    def creating_login_request(self,user_data):
        request = self.factory.post( path='/auth', data=user_data, content_type='application/json')
        request.method = 'LOGIN'
        responce = Auth(request)
        return responce
    # done
    def test_authentication(self):
        response = self.creating_login_request(self.admin_data)
        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Successfully logged in",response.content.decode().replace('"',''))

        new_admin_data = self.admin_data.copy()
        new_admin_data["password"] = "wrong_data"
        response = self.creating_login_request(new_admin_data)
        self.assertEquals(status.HTTP_406_NOT_ACCEPTABLE,response.status_code)
        self.assertEquals("Login or pass is incorrect2",response.content.decode().replace('"',''))
        
        new_admin_data["login"] = "wrong_data"
        response = self.creating_login_request(new_admin_data)
        self.assertEquals(status.HTTP_406_NOT_ACCEPTABLE,response.status_code)
        self.assertEquals("Login or pass is incorrect",response.content.decode().replace('"',''))

    # done
    def test_cookies(self):
        response = self.creating_login_request(self.admin_data)
        request = self.factory.post(path='/auth', data=self.admin_data, content_type='application/json' )
        request.method = 'TESTING_METHOD'

        for key, value in response.cookies.items():
            if key == "token":
                token = jwt.encode({
                'salt': secrets.token_urlsafe(32),
                'creation_date': date(2022,12,4).strftime("%x"),
                'login': "invalid_login",
                'password': self.admin_data["password"]
            }, SECRET_KEY, algorithm='HS256')
                request.COOKIES[key] = token
            else:
                request.COOKIES[key] = value.value

        response = Auth(request)

        self.assertEquals(status.HTTP_401_UNAUTHORIZED,response.status_code)
        self.assertEquals("Invalid token.",response.content.decode().replace('"',''))

        response = self.creating_login_request(self.admin_data)
        request = self.factory.post(path='/auth', data=self.admin_data, content_type='application/json' )
        request.method = 'TESTING_METHOD'

        for key, value in response.cookies.items():
            if key == "token":
                token = jwt.encode({
                'salt': secrets.token_urlsafe(32),
                'creation_date': datetime.today().strftime("%x"),
                'login': self.admin_data["login"],
                'password': "invalid_password"
            }, SECRET_KEY, algorithm='HS256')
                request.COOKIES[key] = token
            else:
                request.COOKIES[key] = value.value

        response = Auth(request)

        self.assertEquals(status.HTTP_401_UNAUTHORIZED,response.status_code)
        self.assertEquals("Invalid token.",response.content.decode().replace('"',''))


        response = self.creating_login_request(self.admin_data)
        request = self.factory.post(path='/auth', data=self.admin_data, content_type='application/json' )
        request.method = 'TESTING_METHOD'

        for key, value in response.cookies.items():
            if key == "token":
                token = jwt.encode({
                'salt': secrets.token_urlsafe(32),
                'creation_date': (date.today() - timedelta(days=1)).strftime("%x"),
                'login': self.admin_data["login"],
                'password': User.objects.get(login=self.admin_data["login"]).password
            }, SECRET_KEY, algorithm='HS256')
                request.COOKIES[key] = token
            else:
                request.COOKIES[key] = value.value

        response = Auth(request)

        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Method is not defined.",response.content.decode().replace('"',''))

    # done
    def test_creating_user(self):
        create_user_data  = {
            "login":"user1",
            "password":"mypassword1",
            "is_superuser":"False",
            "can_edit":"False"
            }
        
        response = self.creating_login_request(self.admin_data)
        request = self.factory.post(path='/auth', data=create_user_data, content_type='application/json' )
        request.method = 'CREATE_USER'
        for key, value in response.cookies.items():
            request.COOKIES[key] = value.value
        response = Auth(request)

        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Successfully registered",response.content.decode().replace('"',''))

        response = self.creating_login_request(self.admin_data)
        invalid_create_user_data = create_user_data.copy()
        invalid_create_user_data["no valid field"] = "no valid value"
        request = self.factory.post(path='/auth', data=invalid_create_user_data, content_type='application/json' )
        request.method = 'CREATE_USER'
        for key, value in response.cookies.items():
            request.COOKIES[key] = value.value
        response = Auth(request)

        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Wrong data.",response.content.decode().replace('"',''))
    # done
    def test_editing_user(self):
        edit_user_data = {
            "login":"user2",
            "password":"mypassword2",
            "is_superuser":"False",
            "can_edit":"False"
            }
        user = UserSerializer(data=edit_user_data)
        if user.is_valid():
            user.save()
        edit_user_data["id"] = User.objects.get(login=edit_user_data["login"]).__dict__["id"]

        response = self.creating_login_request(self.admin_data)
        # data = User.objects.values()
        # responsee = []
        # for temp in data:
        #     responsee.append(temp)
        # print(responsee)

        new_edit_user_data = edit_user_data.copy()
        new_edit_user_data["password"] +="_add_data"
        request = self.factory.post(path='/auth', data=edit_user_data, content_type='application/json' )
        request.method = 'EDIT_USER'
        for key, value in response.cookies.items():
            request.COOKIES[key] = value.value
        response = Auth(request)

        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Successfully edit",response.content.decode().replace('"',''))


        new_edit_user_data = edit_user_data.copy()
        new_edit_user_data["id"] = 9999999
        request = self.factory.post(path='/auth', data=new_edit_user_data, content_type='application/json' )
        request.method = 'EDIT_USER'
        for key, value in response.cookies.items():
            request.COOKIES[key] = value.value
        response = Auth(request)

        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Wrong data.",response.content.decode().replace('"',''))


    # done
    def test_deleting_user(self):
        delete_user_data  = {
            "login":"user3",
            "password":"mypassword3",
            "is_superuser":"False",
            "can_edit":"False"
            }
        new_user = UserSerializer(data=delete_user_data)
        if new_user.is_valid():
            new_user.save()
        delete_user_data["id"] = User.objects.get(login=delete_user_data["login"]).__dict__["id"]

        response = self.creating_login_request(self.admin_data)
        new_delete_data = delete_user_data.copy()
        new_delete_data["id"] = 999999
        request = self.factory.post(path='/auth', data=new_delete_data, content_type='application/json' )
        request.method = 'DELETE_USER'
        for key, value in response.cookies.items():
            request.COOKIES[key] = value.value
        response = Auth(request)

        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("User is not found.",response.content.decode().replace('"',''))


        response = self.creating_login_request(self.admin_data)
        request = self.factory.post(path='/auth', data=delete_user_data, content_type='application/json' )
        request.method = 'DELETE_USER'
        for key, value in response.cookies.items():
            request.COOKIES[key] = value.value
        response = Auth(request)

        self.assertEquals(status.HTTP_200_OK,response.status_code)
        self.assertEquals("Successfully delete.",response.content.decode().replace('"',''))

    # done
    def test_users_list(self):
        response = self.creating_login_request(self.admin_data)
        new_request = self.factory.post(path='/auth', data=self.admin_data, content_type='application/json' )
        new_request.method = 'USER_LIST'
        for key, value in response.cookies.items():
            new_request.COOKIES[key] = value.value
        response = Auth(new_request)
        self.assertEquals(status.HTTP_200_OK,response.status_code)
