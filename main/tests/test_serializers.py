from django.test import TestCase

from ..models import User
from ..serializers import UserSerializer

class UserSerializerTestCase(TestCase):
    def test_user(self):
        user_1 = User.objects.create(login="user1", password="password1", is_superuser=True,can_edit=True)
        user_2 = User.objects.create(login="user2", password="password2", is_superuser=True,can_edit=False)
        user_3 = User.objects.create(login="user3", password="password3", is_superuser=False,can_edit=True)
        user_4 = User.objects.create(login="user4", password="password4", is_superuser=False,can_edit=False)
        data = UserSerializer([user_1,user_2,user_3,user_4], many=True).data
        expected_data = [
            {
            'login': 'user1',
            'password':'password1',
            'is_superuser': True,
            'can_edit': True
            },
            {
            'login': 'user2',
            'password':'password2',
            'is_superuser': True,
            'can_edit': False
            },
            {
            'login': 'user3',
            'password':'password3',
            'is_superuser': False,
            'can_edit': True
            },
            {
            'login': 'user4',
            'password':'password4',
            'is_superuser': False,
            'can_edit': False
            },
        ]
        self.assertEquals(expected_data, data)