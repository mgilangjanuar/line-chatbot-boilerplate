import os
from wit import Wit
from linebot import (
    LineBotApi,
    WebhookHandler
)
from dotenv import (
    load_dotenv,
    find_dotenv
)
from linebot.models import *
from lib import (
    StandardClient,
    TextClient,
    SimpleWitClient,
    AdvancedWitClient
)


load_dotenv(find_dotenv())

class ChatbotHandler():

    def __init__(self, load_clients, redis=None):
        self.handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))
        self.bot = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
        load_clients(ClientHandler(self.handler, self.bot, redis)).start()

    def handle(self, request, logger=None):
        body = request.get_data(as_text=True)
        if (logger):
            logger.info('Request body: {}'.format(body))
        self.handler.handle(body, request.headers.get('X-Line-Signature'))


class ClientHandler():

    def __init__(self, handler, bot, redis=None):
        self.handler = handler
        self.bot = bot
        self.redis = redis
        self.entities = {}
        self.options = {}

    def add(self, client, events, options={}):
        options['__redis__'] = self.redis
        self.options[client] = options
        for entity in events:
            if (entity.message):
                if (not entity.event in self.entities):
                    self.entities[entity.event] = {}
                if (not entity.message in self.entities[entity.event]):
                    self.entities[entity.event][entity.message] = []
                self.entities[entity.event][entity.message].append(client)
            else:
                if (not entity.event in self.entities):
                    self.entities[entity.event] = []
                self.entities[entity.event].append(client)

    def start(self):
        @self.handler.add(MessageEvent, message=TextMessage)
        def handle_text_message(event):
            if (MessageEvent in self.entities and TextMessage in self.entities[MessageEvent]):
                execute = False
                for client in self.entities[MessageEvent][TextMessage]:
                    if (isinstance(client, StandardClient) or isinstance(client, TextClient)):
                        execute = client.run(self.bot, event, self.options[client])

                if (not execute and 'WIT_TOKEN' in os.environ):
                    wit_response = Wit(os.environ.get('WIT_TOKEN')).message(event.message.text)
                    for client in self.entities[MessageEvent][TextMessage]:
                        if (isinstance(client, SimpleWitClient) or isinstance(client, AdvancedWitClient)):
                            self.options[client]['wit_response'] = wit_response
                            client.run(self.bot, event, self.options[client])

        @self.handler.add(MessageEvent, message=StickerMessage)
        def handle_sticker_message(event):
            if (MessageEvent in self.entities and StickerMessage in self.entities[MessageEvent]):
                for client in self.entities[MessageEvent][StickerMessage]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(MessageEvent, message=ImageMessage)
        def handle_image_message(event):
            if (MessageEvent in self.entities and ImageMessage in self.entities[MessageEvent]):
                for client in self.entities[MessageEvent][ImageMessage]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(MessageEvent, message=VideoMessage)
        def handle_video_message(event):
            if (MessageEvent in self.entities and VideoMessage in self.entities[MessageEvent]):
                for client in self.entities[MessageEvent][VideoMessage]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(MessageEvent, message=AudioMessage)
        def handle_audio_message(event):
            if (MessageEvent in self.entities and AudioMessage in self.entities[MessageEvent]):
                for client in self.entities[MessageEvent][AudioMessage]:
                    client.run(self.bot, event, self.options[client])
        
        @self.handler.add(MessageEvent, message=LocationMessage)
        def handle_location_message(event):
            if (MessageEvent in self.entities and LocationMessage in self.entities[MessageEvent]):
                for client in self.entities[MessageEvent][LocationMessage]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(MessageEvent, message=FileMessage)
        def handle_file_message(event):
            if (MessageEvent in self.entities and FileMessage in self.entities[MessageEvent]):
                for client in self.entities[MessageEvent][FileMessage]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(FollowEvent)
        def handle_follow(event):
            if (FollowEvent in self.entities):
                for client in self.entities[FollowEvent]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(UnfollowEvent)
        def handle_unfollow(event):
            if (UnfollowEvent in self.entities):
                for client in self.entities[UnfollowEvent]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(JoinEvent)
        def handle_join(event):
            if (JoinEvent in self.entities):
                for client in self.entities[JoinEvent]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(LeaveEvent)
        def handle_leave(event):
            if (LeaveEvent in self.entities):
                for client in self.entities[LeaveEvent]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(PostbackEvent)
        def handle_postback(event):
            if (PostbackEvent in self.entities):
                for client in self.entities[PostbackEvent]:
                    client.run(self.bot, event, self.options[client])

        @self.handler.add(BeaconEvent)
        def handle_beacon(event):
            if (BeaconEvent in self.entities):
                for client in self.entities[BeaconEvent]:
                    client.run(self.bot, event, self.options[client])
