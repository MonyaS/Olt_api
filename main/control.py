from datetime import datetime, timedelta
import jwt
from bson.objectid import ObjectId
from dictdiffer import diff
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from OLT.settings import SECRET_KEY
from base_connection import get_db_handle
from main.models import User, Olt
from main.serializers import OLTSerializer
from main.auth import return_response


@csrf_exempt
def OLTApi(request):
    try:
        olt_data = JSONParser().parse(request)

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

        if request.method == 'GET_OLTS':
            data = Olt.objects.values()
            response = []
            for temp in data:
                response.append(temp)
            return return_response(response, cookie, user_name)

        if request.method == 'GET_OLT':
            olt = Olt.objects.filter(ip=olt_data["ip"]).first().__dict__
            if not user.can_edit:
                olt.pop("ip")
                olt.pop("login")
                olt.pop("password")
            return return_response(olt, cookie, user_name)
        
        elif request.method == 'CREATE_OLT' and user.can_edit:
            serializer = OLTSerializer(data=olt_data)
            if serializer.is_valid():
                serializer.save()
                return return_response(f"OLT added successfully.", cookie, user_name)
            else:
                print(serializer.errors)
                #вывод  при неправильных данных???????????????
                return return_response("Fail to add OLT. This ip already exists.", cookie, user_name)

        elif request.method == 'UPDATE_OLT' and user.can_edit:
            edit_olt = Olt.objects.filter(_id=olt_data["_id"]).first()
            if edit_olt:
                edit_olt.__dict__.update(olt_data)
                edit_olt.save()
                return return_response("Successfully edit", cookie, user_name)
            else:
                return return_response("Wrong data.", cookie, user_name)

        elif request.method == 'DELETE_OLT' and user.can_edit:
            delete_olt = Olt.objects.filter(_id=olt_data["_id"]).first()
            if delete_olt:
                delete_olt.delete()
                return return_response("Successfully delete.", cookie, user_name)
            else:
                return return_response("User is not found.", cookie, user_name)

        else:
            return return_response("Method is not defined.", cookie, user_name)
    except KeyError:
        return JsonResponse("Some data is wrong.", safe=False, status=500)
    except (jwt.exceptions.DecodeError,jwt.exceptions.InvalidTokenError, AttributeError):
        return JsonResponse("Invalid token.", safe=False, status=401)
    except Exception as err:
        return JsonResponse(f"An error occurred: {err}", safe=False, status=500)