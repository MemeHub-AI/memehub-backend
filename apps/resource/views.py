from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from extension import publish_by_mode
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from extension import Web3JSONEncoder, json_to_str


@api_view(["GET", "POST"])
@parser_classes([JSONParser])
def log_notify(request):

    data = request.data.get("data") or {}
    print(data)
    publish_by_mode(json_to_str(data))

    return Response(
        {"code": 200, "message": "ok", "data": None}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
@parser_classes([JSONParser])
def ping(request):
    return Response(
        {"code": 200, "message": "ok", "data": None}, status=status.HTTP_200_OK
    )
