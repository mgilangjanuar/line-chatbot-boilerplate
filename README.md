LINE Chatbot Boilerplate
========================

## Requirements

 - Python 3.5
 - Redis 4.0.8
 - MongoDB 2.6.10
 - LINE@ Messaging API
 - Wit.ai (optional)

## How to Install (with Yeoman)

 - Install Yeoman

```
npm install -g yo
```

 - Install generator-line-chatbot-boilerplate

```
npm install -g generator-line-chatbot-boilerplate
```

 - Run line-chatbot-boilerplate generator with Yeoman

```
yo line-chatbot-boilerplate
```

## Architecture Flow

![](chatbot_architecture.png?raw=true)

## Guide and Example

### Configuration in `index.py`

```python
from mongoengine import connect
from lib import ChatbotHandler
import redis

...

# create connection to MongoDB
connect('poc_chatbot_boilerplate', host='localhost', port=27017, username=None, password=None)

# connect to Redis server
my_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

# define bot handler
bot_handler = ChatbotHandler(load_clients, redis=my_redis)

...
```

### Create Module

Create a client in `./modules` and create **client object** with methods in it.

**Client Types:**

 - StandardClient

```python
from linebot.models import TextSendMessage
from lib import StandardClient


client = StandardClient(__name__)

@client.on_command(sources=['user'])    # only trigger from user, default: all
def action_ping():                      # name of the method must have "action_" as prefix
    """
    Always reply /pong whatever user type, StandardClient only
    have one on_command decorator method
    """
    client.bot.reply_message(
        client.event.reply_token,
        TextSendMessage(text='/pong')
    )
```

 - TextClient

```python
from linebot.models import TextSendMessage
from lib import TextClient


client = TextClient(__name__)

@client.on_command('ping', sources=['user'])
def action_ping():
    """
    Always reply "/pong" when user type "/ping", TextClient
    only can be registered for TextMessage in register.py
    """
    client.bot.reply_message(
        client.event.reply_token,
        TextSendMessage(text='/pong')
    )
```

 - SimpleWitClient

```python
from linebot.models import TextSendMessage
from lib import SimpleWitClient


client = SimpleWitClient(__name__)

@client.on_command('greeting')
def action_greeting(value):
    """Reply a string when entity greeting is True
    """
    if (value == 'True'):
        client.bot.reply_message(
            client.event.reply_token,
            TextSendMessage(text='Nice to meet you!')
        )
```

 - AdvancedWitClient

```python
from linebot.models import TextSendMessage
from lib import AdvancedWitClient


client = AdvancedWitClient(__name__)

@client.on_command('greeting', 'True')
def action_greeting():
    """Reply a string when entity greeting is True
    """
    client.bot.reply_message(
        client.event.reply_token,
        TextSendMessage(text='Nice to meet you!')
    )
```

**Notes:**

 If you doesn't like the prefix '/' for command in TextClient or the prefix "action_" in methods, you can change that in `./lib/client.py`

**Routing Client Methods:**

 - On Command

Run method on command triggered

```python
from linebot.models import TextSendMessage
from lib import TextClient


client = TextClient(__name__)

@client.on_command('echo')
def action_echo(args):
    """
    Echoing an argument when command /echo triggered, for 
    example when user type "/echo some shitty string here"
    will be replied with "some shitty string here"
    """
    client.bot.reply_message(
        client.event.reply_token,
        TextSendMessage(text=args)
    )
```

 - On State

Run method when user/room/group has a state which corresponds to the client's state

```python
from linebot.models import TextSendMessage
from lib import TextClient


client = TextClient(__name__)

@client.on_command('echo')
def action_echo():      # we don't need any arguments
    """Set the state to "echo/input"
    """
    client.state.set_state('echo/input')
    client.state.set_data('go to the action_echo_input() method')
    client.bot.reply_message(
        client.event.reply_token,
        TextSendMessage(text='Please input your string')
    )

@client.on_state('echo/input')
def action_echo_input():
    """
    Always echoing the user's message when his state is "echo/input"
    and delete the state when user type "/end"
    """
    print(client.state.get_data())
    message = client.event.message.text
    if (message == '/end'):
        client.state.delete_state()
        client.state.delete_data()
    else:
        client.bot.reply_message(
            client.event.reply_token,
            TextSendMessage(text=message)
        )
```

### Registering a Client

Update method `load_clients` in `register.py` and define which events (and message types, if any) that will handling your client

Example:

```python
def load_clients(client_handler):
    ...
    # registering ping.client to TextMessage and StickerMessage handler
    client_handler.add(ping.client, [
        EventEntity(MessageEvent, message=TextMessage),
        EventEntity(MessageEvent, message=StickerMessage)
    ])
    ...
    return client_handler
```

## References
 - [LINE@ Messaging API References](https://developers.line.biz/en/reference/messaging-api/)
 - [LINE SDK for Python](https://github.com/line/line-bot-sdk-python)
 - [MongoEngine API Reference](http://docs.mongoengine.org/apireference.html)
