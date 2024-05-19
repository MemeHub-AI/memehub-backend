from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.coin.models import Coin
from web3 import Web3
from extension import str_to_json, json_to_str, cal_market_cap
from memehub.settings import CHAINLIST as ChainList
import logging
import time


class Command(BaseCommand):
    help = "consume_coin"

    def handle(self, *args, **options):
        while True:
            good_dict = {}
            create_info = []
            coins = Coin.objects.filter(status=2).all()
            for coin in coins:
                web3_instance = Web3(
                    Web3.HTTPProvider(ChainList[coin.chain]["rpc"])
                )
                try:
                    t = web3_instance.eth.get_transaction(coin.hash)
                    if t:
                        if good_dict.get(coin.chain):
                            good_dict[coin.chain]["id_list"].append(coin.id)
                        else:
                            good_dict[coin.chain]["id_list"] = [coin.id]
                            good_dict[coin.chain]["market_cap"] = cal_market_cap(
                                coin.chain, web3_instance
                            )

                        create_info.append(
                            {
                                "wallet_address": coin.creater.wallet_address,
                                "symbol": coin.symbol,
                                "create_time": coin.create_time,
                            }
                        )
                except Exception as e:
                    logging.error(e)
                    pass

            if good_dict:

                for key in good_dict.keys():
                    Coin.objects.filter(id__in=good_dict[key]["id_list"]).update(
                        status=1, market_cap=good_dict[key]["market_cap"]
                    )

                create_cache = str_to_json(cache.get("meme_hub:create_cache"))
                create_cache += create_info
                cache.set("meme_hub:create_cache", json_to_str(create_cache), 300)

            time.sleep(60)
