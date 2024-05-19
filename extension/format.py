import typing
from decimal import Decimal
from hexbytes import HexBytes
from web3.datastructures import AttributeDict
from django.conf import settings
import json
import time
import asyncio
import uuid

__all__ = ["Web3JSONEncoder", "time_to_str", "str_to_json", "json_to_str", "wait","get_url_by_chain","create_uuid"]


class Web3JSONEncoder(json.JSONEncoder):
    def default(self, o: typing.Any) -> typing.Any:
        if isinstance(o, bytes):
            return "0x" + o.hex()
        elif isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, HexBytes):
            return o.hex()
        elif isinstance(o, AttributeDict):
            return dict(o)
        return super().default(o)


def get_lan_content(language):
    return {
        "en": {"word": ("swap", "for"), "amount": " a few "},
        "zh": {"word": ("用", "换了"), "amount": "少量 "},
    }[language]


def format_amount(amount, desc):
    amount = round(amount, 2)
    amount = desc if amount <= 0.01 else f" {amount}"
    return amount


def get_content(row, lan_content, name_list):
    currency_amount = format_amount(row["currency_amount"], lan_content["amount"])
    side_amount = format_amount(row["side_amount"], lan_content["amount"])

    name = name_list[row["sender"]] or row["sender"][-5:-1]
    content = f'{name} {lan_content["word"][0]}{currency_amount}{row["currency_symbol"]} {lan_content["word"][1]}{side_amount} {row["side_symbol"]}'

    return content


def get_create_info(coin):
    pass


def time_to_str(time, fmt="%Y-%m-%d %H:%M:%S"):
    return time.strftime(fmt)


def str_to_json(str, default=[]):
    try:
        return json.loads(str)
    except:
        return default


def json_to_str(d):
    return json.dumps(d)


async def wait(seconds):
    await asyncio.sleep(seconds)


def get_url_by_chain(address, chain, sub_prefix="address"):
    return f"{settings.OutsideUrl[chain]}{sub_prefix}{address}"


def create_uuid(string, namespace=uuid.uuid1()):
    return uuid.uuid5(namespace,string)