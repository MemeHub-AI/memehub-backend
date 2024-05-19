import jwt
from jwt import exceptions
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import APIException
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from django.conf import settings
from apps.user.models import User

class MyAuthenticationFailed(APIException):
    status_code = status.HTTP_200_OK
    default_detail = {'code': 400, 'message': 'error', 'data': None}

    def __init__(self, detail=None):
        if not isinstance(detail, dict):
            detail = self.default_detail

        self.detail = self.my_get_error_details(detail)

    def my_get_error_details(self, data):
        if isinstance(data, list):
            ret = [self.my_get_error_details(item) for item in data]
            if isinstance(data, ReturnList):
                return ReturnList(ret, serializer=data.serializer)
            return ret
        elif isinstance(data, dict):
            ret = {
                key: self.my_get_error_details(value)
                for key, value in data.items()
            }
            if isinstance(data, ReturnDict):
                return ReturnDict(ret, serializer=data.serializer)
            return ret

        return data


class JWTHeadersAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        if (request.method == 'POST' and request.path == '/api/v1/user/users/') or (request.method == 'GET' and request.path.startswith('/api/v1/coin/coins')):
            return None
        token = request.META.get('HTTP_AUTHORIZATION')
        # print("token",token)
        if not token:
            raise MyAuthenticationFailed({
                'code': 400,
                'message': 'User not logged in',
                'data': None
            })

        
        payload = parse_payload(token)
        print(payload)
        if payload["status"]:
            try:
                user = User.objects.get(id=payload['data']['user_id'])
                if payload['data']["sign"] != user.sign:
                    raise MyAuthenticationFailed({
                        'code': 400,
                        'message': 'invalid sign',
                        'data': None
                    })
            except Exception:
                raise MyAuthenticationFailed({
                    'code': 400,
                    'message': 'token expired',
                    'data': None
                })

            return user, payload["data"]
        else:
            raise MyAuthenticationFailed({
                'code': 400,
                'message': payload['error'],
                'data': None
            })
        

    def authenticate_header(self, request):
        return 'token error'


def parse_payload(token):
    result = {"status":False,"data":None,"error":None}
    try:
        token = token.split(" ")[1]
        verified_payload = jwt.decode(token,settings.SALT,algorithms = ['HS256'])
        result["status"] = True
        result['data']=verified_payload
    except exceptions.ExpiredSignatureError:
        result['error'] = 'token expired'
    except jwt.DecodeError:
        result['error'] = 'token decode error'
    except jwt.InvalidTokenError:
        result['error'] = 'invalid token'
    except Exception as e:
        result['error'] = str(e)
    return result