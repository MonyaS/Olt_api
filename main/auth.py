from datetime import datetime, timedelta

import jwt
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from OLT.settings import SECRET_KEY
from main.models import User
from main.serializers import UserSerializer


def return_response(massage, cookie, user_name):
    response = JsonResponse(massage, safe=False)
    response.set_cookie(key='token', value=cookie, httponly=True, expires=datetime.today() + timedelta(days=365))
    response.set_cookie(key='user_name', value=user_name, httponly=True, expires=datetime.today() + timedelta(days=365))
    return response


@csrf_exempt
def Auth(request):
    try:
        user_data = JSONParser().parse(request)

        if request.method == 'LOGIN':
            user = User.objects.filter(login=user_data["login"]).first()
            if user is None:
                return JsonResponse("Login or pass is incorrect", safe=False)
            if not user.check_password(user_data["password"]):
                return JsonResponse("Login or pass is incorrect", safe=False)
            return return_response("Successfully logged in", user.token, user.login)

        cookie = request.COOKIES.get('token')
        user_name = request.COOKIES.get('user_name')
        token_data = jwt.decode(cookie, SECRET_KEY, algorithms=['HS256'])
        creation_date = datetime.strptime(token_data["creation_date"], "%x")
        user = User.objects.filter(login=token_data['login']).first()
        if creation_date < datetime.today() - timedelta(days=7):
            raise jwt.exceptions.InvalidTokenError
        if not user.password == token_data['password']:
            raise jwt.exceptions.InvalidTokenError
        if creation_date <= datetime.today() - timedelta(days=1):
            cookie = user.token

        if request.method == 'USER_LIST' and user.is_superuser:
            data = User.objects.values()
            response = []
            for temp in data:
                response.append(temp)
            return return_response(response, cookie, user_name)

        elif request.method == 'CREATE_USER' and user.is_superuser:
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                return return_response("Successfully registered", cookie, user_name)
            else:
                return return_response("Wrong data.", cookie, user_name)

        elif request.method == 'EDIT_USER' and user.is_superuser:
            edit_user = User.objects.get(id=user_data["id"])
            if edit_user:
                if "password" in user_data.keys():
                    edit_user.set_password(user_data["password"])
                    user_data.pop("password")
                edit_user.__dict__.update(user_data)
                edit_user.save()
                return return_response("Successfully edit", cookie, user_name)
            else:
                return return_response("Wrong data.", cookie, user_name)

        elif request.method == 'DELETE_USER' and user.is_superuser:
            delete_user = User.objects.filter(id=user_data["id"]).first()
            if delete_user:
                delete_user.delete()
                return return_response("Successfully delete.", cookie, user_name)
            else:
                return return_response("User is not found.", cookie, user_name)

        else:
            return return_response("Method is not defined.", cookie, user_name)
    except KeyError:
        return JsonResponse("Some data is wrong.", safe=False)
    except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError):
        return JsonResponse("Invalid token.", safe=False)
    except Exception as err:
        return JsonResponse(f"An error occurred: {err}", safe=False)
