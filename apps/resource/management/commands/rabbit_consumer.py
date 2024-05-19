from web3 import Web3
import typing
from decimal import Decimal
import json
from extension import load_abi_events, load_abi, str_to_json, json_to_str, consume_by_rabbit
from resource.models import ERC20Token, Log, CoinHoldInfo
from real_data.models import Transaction
from django.core.management.base import BaseCommand
from django.core.cache import cache
from hexbytes import HexBytes
from memehub.settings import CHAINLIST as ChainList
import asyncio


WEB3 = Web3()
ABI_EVENTS = load_abi_events(WEB3)
ABI = load_abi()



def get_erc20_onchain(web3: Web3, address: str):
    contract = web3.eth.contract(address, abi=ABI["Erc20"])
    name = contract.functions.name().call()
    symbol = str(contract.functions.symbol().call())
    decimals = int(contract.functions.decimals().call())
    totalSupply = int(contract.functions.totalSupply().call())
    return name, symbol, decimals, totalSupply


def get_erc20_token(web3: Web3, address: str, chain_id: int):

    erc20_token = ERC20Token.objects.filter(chain_id=chain_id, address=address).first()

    if not erc20_token:
        name,symbol,decimals,totalSupply =  get_erc20_onchain(web3, address)        
        erc20_token = ERC20Token(
            id=ERC20Token.create_uuid(chain_id,address),
            chain_id=chain_id,
            address=address,
            name=name,
            symbol=symbol,
            decimals=decimals,
            total_supply=Decimal(totalSupply) / Decimal(10**decimals))
        erc20_token.save()

    return erc20_token


def get_tokens(log):
    web3 = Web3(Web3.HTTPProvider(ChainList[log["chain"]]["rpc"]))
    match log["version"]:
        case "memehubtoken":
            match log["type"]:
                case "ContinuousMint":
                    amount0, amount1 = (
                        log["reserveTokenAmount"],
                        log["continuousTokenAmount"],
                    )
                    token0, token1 = (
                        log["reserveTokenAddress"],
                        log["continuousTokenAddress"],
                    )

                case "ContinuousBurn":
                    amount0, amount1 = (
                        log["continuousTokenAmount"],
                        log["reserveTokenAmount"],
                    )
                    token0, token1 = (
                        log["continuousTokenAddress"],
                        log["reserveTokenAddress"],
                    )

    return (
        get_erc20_token(web3, WEB3.to_checksum_address(token0), log["chain_id"]),
        get_erc20_token(web3, WEB3.to_checksum_address(token1), log["chain_id"]),
        amount0,
        amount1,
    )


def get_swap_info(logs):
    swap_info = {}
    for log in logs:
        token0_obj, token1_obj, amount0, amount1 = get_tokens(log)
        log["amount_to"] = Decimal(amount1) / (10**token1_obj.decimals)
        log["symbol_to"] = token1_obj.symbol
        log["currency_to"] = token1_obj.address

        if not swap_info:
            log["amount_from"] = Decimal(amount0) / (10**token0_obj.decimals)
            log["symbol_from"] = token0_obj.symbol
            log["currency_from"] = token0_obj.address

            swap_info.update(**log)
        else:
            swap_info["amount_to"] = log["amount_to"]
            swap_info["symbol_to"] = log["symbol_to"]
            swap_info["currency_to"] = log["currency_to"]

    swap_info["amount_to"] = abs(Decimal(swap_info["amount_to"]))
    swap_info["amount_from"] = abs(Decimal(swap_info["amount_from"]))
    return swap_info


def update_hold_info(transaction):
    info = CoinHoldInfo.objects.filter(
        wallet_address=transaction.account,
        token_address=transaction.base_address,
    )
    if info.exists():
        info = info.first()
        hold_amount = Decimal(info.hold_amount)
        if transaction.type == "buy":
            info.hold_amount = hold_amount + transaction.base_amount
        else:
            info.hold_amount = hold_amount - transaction.base_amount
            if info.hold_amount <= 0:
                info.hold_amount = 0

    else:
        info = CoinHoldInfo(
            wallet_address=transaction.account,
            token_address=transaction.base_address,
        )
        info.hold_amount = transaction.base_amount

    info.save()


def filter_transaction(t):
    event_name = t["event_name"]
    p_version = t.get("p_version", "memehubtoken")
    logs = t["log"]

    t["resolved_log"] = []
    for log in logs:
        topics = [HexBytes(_) for _ in log["topics"]]

        event = ABI_EVENTS[p_version][event_name]
        topic0: str = event["topic0"]
        
        if topics[0].hex() != topic0:
            return {}

        # decode data in key:topic first
        # print("topic",topics[1:])
        resolved_log = {
            input["name"]: WEB3.codec.decode([input["type"]], topic)[0]
            for input, topic in zip(event["topic_inputs"], topics[1:])
        }

        # decode data in key:data
        tmp_dict = {
            str(input["name"]): str(input["type"]) for input in event["data_inputs"]
        }

        resolved_log.update(
            zip(
                tmp_dict.keys(),
                WEB3.codec.decode(list(tmp_dict.values()), HexBytes(log["data"])),
            )
        )
        resolved_log["version"] = t["p_version"]
        resolved_log["type"] = event_name
        resolved_log["chain_id"] = ChainList[t["chain"]]["id"]
        resolved_log["chain"] = t["chain"]

        t["resolved_log"].append(resolved_log)

    return t


def set_trade_cache(cache_list):
    trade_cache = str_to_json(cache.get("meme_hub:trade_cache"))
    trade_cache += cache_list

    cache.set(
        "meme_hub:trade_cache",
        json_to_str(trade_cache),
        300,
    )


def process_data(body: bytes):
    # print("process_data",body)
    transactions: list = json.loads(body)
    cache_list = []

    try:
        for t in transactions:
            t["p_version"] = t.get("p_version").lower()# process old data, remove after that
            t = filter_transaction(t)
            if t:
                swap_info = get_swap_info(t["resolved_log"])

                for l in t["log"]:
                    Log(**l).save()

                transaction = Transaction(

                    chain=t["chain"],
                    hash=t["log"][0]["transaction_hash"],
                    account=t["resolved_log"][0]["wallet_address"],
                    contract=t["log"][0]["address"],
                    quote_symbol=swap_info["symbol_from"],
                    quote_address=swap_info["currency_from"],
                    quote_amount=swap_info["amount_from"],
                    base_symbol=swap_info["symbol_to"],
                    base_address=swap_info["currency_to"],
                    base_amount=swap_info["amount_to"],
                    type="buy" if "mint" in t["event_name"].lower() else "sell",
                )
                transaction.save()

                update_hold_info(transaction)
                cache_list.append(
                    {
                        "wallet_address": transaction.account,
                        "quote_amount": transaction.quote_amount,
                        "quoto_symbol": transaction.quote_symbol,
                        "base_symbol": transaction.base_symbol,
                        "type": transaction.type,
                    }
                )

    except Exception as e:
        raise e


def rabbitmq_callback(channel, method, properties, body: bytes):
    process_data(body)
    channel.basic_ack(delivery_tag=method.delivery_tag)


class Command(BaseCommand):
    def handle(self, *args, **options):
        consume_by_rabbit(process_data)

