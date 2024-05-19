from .my_rabbit import *
from .utils import *
from .format import *
from .web3_api import *


def publish_by_mode(
    value,
    mode="rabbitmq",
    topic="meme_hub",
):
    match mode:
        case "rabbitmq":
            producer = RabbitServer(
                9,
                topic,
            )
        case "kafka":
            pass
            # producer = KafkaClient()

    producer.publish(topic=topic, value=value)
