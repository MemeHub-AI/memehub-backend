from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.request import HttpRequest
from extension import publish_by_mode
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from extension import Web3JSONEncoder, json_to_str, create_transaction_receipt
import json
import hmac
import hashlib
import base64
import os

quicknode_secrets = {
    1: os.environ.get("QUICKNODE_SECRET_ETH", "7f7f7f7f7f"),
    534352: os.environ.get("QUICKNODE_SECRET_SCROLL", "7f7f7f7f7f"),
}


@api_view(["GET", "POST"])
@parser_classes([JSONParser])
def log_notify(request: HttpRequest):

    ts = request.headers.get('x-qn-timestamp')
    sign = request.headers.get('x-qn-signature')
    nonce = request.headers.get('x-qn-nonce')
    reqid = request.headers.get('x-qn-notificationid')

    if ts and sign and nonce and reqid:
        # By QuickAlert
        chain_id = int(request.GET['chain'])
        req_path = f'/api/v1/log_notify/?chain={chain_id}'
        comp_hash = hashlib.sha256(req_path.encode() + request.body).hexdigest()
        h = hmac.new(quicknode_secrets.get(chain_id, b'7f7f7f7f7f'), (nonce + comp_hash + ts).encode(), digestmod=hashlib.sha256)
        comp_sign = base64.b64encode(h.digest()).decode()
        if comp_sign != sign:
            return Response(
                {"code": 403, "message": "sign failure", "data": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        publish_by_mode(json_to_str([create_transaction_receipt(item) for item in json.loads(request.body)]))
    else:
        # By other
        data = request.data.get("data") or {}
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

