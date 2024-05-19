from django.db import models
import uuid
import socket
from decimal import Decimal
import os


class CommonModel(models.Model):
    chain = None
    id = models.CharField(max_length=36, primary_key=True)

    @classmethod
    def create_uuid(cls, address: str):
        return uuid.uuid5(cls.NAMESPACE, f"{cls.chain}:{address}")

class Block:
    pass


class TxReceipt(CommonModel):
    class Meta:
        db_table = "tx_receipt"

    blockHash = models.CharField(max_length=128)
    blockNumber = models.IntegerField()
    contractAddress = models.CharField(max_length=128)
    cumulativeGasUsed = models.IntegerField()
    effectiveGasPrice = models.IntegerField()
    gasUsed = models.IntegerField()
    address_from = models.CharField(max_length=128)
    logs = models.JSONField()
    root = models.CharField(max_length=255)
    status = models.IntegerField()
    address_to = models.CharField(max_length=128)
    transactionHash = models.CharField(max_length=128)
    transactionIndex = models.IntegerField()
    type = models.IntegerField()


class Log(models.Model):
    class Meta:
        db_table = "log"

    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=128)
    block_hash = models.CharField(max_length=100)
    block_number = models.IntegerField()
    data = models.CharField(max_length=255)
    log_index = models.IntegerField()
    topics = models.JSONField()
    transaction_hash = models.CharField(max_length=128)
    transaction_index = models.IntegerField()
    removed = models.BooleanField()


class ERC20Token(models.Model):
    class Meta:
        db_table = "erc20_token"

    id = models.CharField(max_length=36, primary_key=True)
    address = models.CharField(verbose_name="token address", max_length=60,null=True)
    chain_id = models.IntegerField(verbose_name="chain ID",null=True)
    name = models.CharField(max_length=60,null=True)
    symbol = models.CharField(max_length=60,null=True)
    decimals = models.IntegerField(null=True)
    total_supply = models.DecimalField(
        max_digits=65, decimal_places=18
    )
    oracle = models.CharField(max_length=60,null=True)
    oracle_type = models.SmallIntegerField(default=0,null=True)

    NAMESPACE = uuid.uuid5(
        uuid.NAMESPACE_X500, socket.gethostname() + f"/EVMErc20/{os.getpid()}"
    )

    @classmethod
    def create_uuid(cls, chain_id: int, address: str):
        return uuid.uuid5(cls.NAMESPACE, f"{chain_id}:{address}")

class CoinHoldInfo(models.Model):
    id = models.AutoField(primary_key=True)
    wallet_address = models.CharField(max_length=60)
    token_address = models.CharField(
        max_length=60
    )
    hold_amount = models.FloatField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coin_hold_info"

