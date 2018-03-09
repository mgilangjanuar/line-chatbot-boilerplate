from linebot.models import *
from modules import *
from lib import EventEntity


def load_clients(client_handler):
    # log all text message
    client_handler.add(log.client, [
        EventEntity(MessageEvent, message=TextMessage)
    ])

    # registering ping.client to TextMessage and StickerMessage handler
    client_handler.add(ping.client, [
        EventEntity(MessageEvent, message=TextMessage),
        EventEntity(MessageEvent, message=StickerMessage)
    ])

    return client_handler
