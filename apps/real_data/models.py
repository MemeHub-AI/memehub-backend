from django.db import models
from django.conf import settings
from channels.db import database_sync_to_async

__all__ = ["Transaction"]


class Transaction(models.Model):

    id = models.AutoField(primary_key=True)
    chain = models.CharField(max_length=20)
    hash = models.CharField(max_length=128)
    account = models.CharField(max_length=128)
    contract = models.CharField(max_length=128)
    publish_time = models.DateTimeField(auto_now_add=True)
    quote_symbol = models.CharField(max_length=128, null=True)
    quote_address = models.CharField(max_length=128, null=True)
    quote_amount = models.FloatField(null=True)
    base_symbol = models.CharField(max_length=128, null=True)
    base_address = models.CharField(max_length=128, null=True)
    base_amount = models.FloatField(null=True)
    type = models.CharField(max_length=10, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transaction"
        constraints = [
            models.UniqueConstraint(fields=["chain", "hash"], name="unique_trade")
        ]

    @classmethod
    def get_trade_log(cls, offset=5):
        logs = cls.objects.order_by("-create_time")[:offset]

        pass

    @classmethod
    async def get_latest_transaction(cls, token_address, offset=5):
        tx = await database_sync_to_async(list)(cls.objects.filter(base_address=token_address).order_by("-create_time")[:5])
        if tx:
            ts = {"quote_symbol": tx[0].quote_symbol, "base_sumbol": tx[0].base_symbol}
            ts["records"] = [
                {
                    "account": _.account,
                    "type": _.type,
                    "quote_amount": _.quote_amount,
                    "base_amount": _.base_amount,
                    "create_time": _.create_time,
                    "hash": _.hash,
                    "hash_url": f"{settings.ChainList[_.chain]}tx/{_.hash}",
                }
                for _ in tx[:offset]
            ]

            return ts
        return {}

    @property
    def currency_amount(self):
        return self.quote_amount if self.type == "buy" else self.base_amount
