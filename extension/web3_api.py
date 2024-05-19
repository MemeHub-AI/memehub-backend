from web3 import Web3
from web3.types import LogReceipt, TxReceipt
from hexbytes import HexBytes
from typing import Any
from django.conf import settings
import json
import os


print(os.listdir())


def load_abi(file=None):
    if file is not None:
        files = [file]
    else:
        files = os.listdir("static")

    return {
        file.split(".")[0].lower(): json.load(open(os.path.join("static", file)))
        for file in files
    }


def load_abi_events(web3_instance):
    ABI = load_abi()
    abi_events = {}
    for p in ABI.keys():
        abi_events[p] = {}
        for abi in ABI[p]:
            if abi["type"] == "event":
                abi_events[p][abi["name"]] = {
                    "topic0": web3_instance.keccak(
                        text=f'{abi["name"]}({",".join([input["type"] for input in abi["inputs"]])})'
                    ).hex(),
                    "topic_inputs": [_ for _ in abi["inputs"] if _["indexed"] is True],
                    "data_inputs": [_ for _ in abi["inputs"] if _["indexed"] is False],
                }

    return abi_events


Aggregator_ABI = load_abi("ChainLink.json")


def cal_market_cap(chain, w3=None):
    chain_config = settings.ChainList[chain]

    if w3 is None:
        w3 = Web3(Web3.HTTPProvider(chain_config["rpc"]))

    aggregator = w3.eth.contract(address=chain_config["aggregator"], abi=Aggregator_ABI)
    round_data = aggregator.functions.latestRoundData().call()
    return round_data[1] / 10 ** aggregator.functions.decimals().call()


def create_log_entry(data: dict[str, Any]):
    return LogReceipt({
        'address': Web3.to_checksum_address(data['address']),
        'blockHash': HexBytes(data['blockHash']),
        'blockNumber': int(data['blockNumber'], 16),
        'data': HexBytes(data['data']),
        'logIndex': int(data['logIndex'], 16),
        'topics': [HexBytes(topic) for topic in data['topics']],
        'transactionHash': HexBytes(data['transactionHash']),
        'transactionIndex': int(data['transactionIndex'], 16),
        'removed': bool(data['removed'])
    })


def create_transaction_receipt(data: dict[str, Any]):
    return TxReceipt({
        'transactionHash': HexBytes(data['transactionHash']),
        'transactionIndex': int(data['transactionIndex'], 16),
        'blockHash': HexBytes(data['blockHash']),
        'blockNumber': int(data['blockNumber'], 16),
        'contractAddress': Web3.to_checksum_address(data['contractAddress']) if data.get('contractAddress') else None,
        'cumulativeGasUsed': int(data['cumulativeGasUsed'], 16),
        'effectiveGasPrice': int(data['effectiveGasPrice'], 16),
        'gasUsed': int(data['gasUsed'], 16),
        'from': Web3.to_checksum_address(data['from']),
        'to': Web3.to_checksum_address(data['to']) if data.get('to') else None,
        'logs': [create_log_entry(log) for log in data['logs']],
        'logsBloom': HexBytes(data['logsBloom']),
        'status': int(data['status'], 16),
        'root': HexBytes(data['root']) if data.get('root') else None,
        'type': int(data['type'], 16)
    })
