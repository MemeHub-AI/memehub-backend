from web3 import Web3, types
from django.conf import settings
import json
import os

__all__ = ["load_abi", "load_abi_events", "cal_market_cap"]

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


    
