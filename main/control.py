from datetime import datetime, timedelta
import rest_framework
import jwt
from bson.objectid import ObjectId
from dictdiffer import diff
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from OLT.settings import SECRET_KEY
from base_connection import get_db_handle
from main.models import User
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
            response = []
            for temp in list(get_db_handle().find({}, {'ip': True})):
                temp['_id'] = str(temp['_id'])
                response.append(temp)
            return return_response(response, cookie, user_name)

        if request.method == 'GET_OLT':
            response = get_db_handle().find({"_id": ObjectId(olt_data["_id"])}, {'_id': False})
            if user.can_edit:
                try:
                    response.pop("access")
                except:
                    pass
            return return_response(list(response), cookie, user_name)

        elif request.method == 'CREATE_OLT' and user.can_edit:
            if not list(get_db_handle().find({'ip': olt_data['ip']})):
                if olt_data['login'] and olt_data['password']:
                    status = get_db_handle().insert_one(olt_data)
                    return return_response(f"OLT added successfully.{status}", cookie, user_name)
            else:
                return return_response("Fail to add OLT. This ip already exists.", cookie, user_name)

        elif request.method == 'UPDATE_OLT' and user.can_edit:
            result = diff(get_db_handle().find_one({"_id": ObjectId(olt_data["_id"])}, {'_id': False}), olt_data)
            id = olt_data.pop("_id")
            get_db_handle().replace_one({"_id": ObjectId(id)}, olt_data)
            return return_response(list(result), cookie, user_name)

        elif request.method == 'DELETE_OLT' and user.can_edit:
            response = get_db_handle().delete_one({"_id": ObjectId(olt_data["Id"])}).deleted_count
            return return_response(f"Deleted {response} object.", cookie, user_name)

        else:
            return return_response("Method is not defined.", cookie, user_name)
    except KeyError:
        return JsonResponse("Some data is wrong.", safe=False)
    except (jwt.exceptions.DecodeError,jwt.exceptions.InvalidTokenError, AttributeError):
        return JsonResponse("Invalid token.", safe=False)
    except Exception as err:
        return JsonResponse(f"An error occurred: {err}", safe=False)