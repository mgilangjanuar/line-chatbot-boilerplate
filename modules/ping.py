from linebot.models import TextSendMessage
from lib import StandardClient


client = StandardClient(__name__)

@client.on_command(sources=['user'])
def action_ping():
    """Always reply /pong whatever you chat
    """
    client.bot.reply_message(
        client.event.reply_token,
        TextSendMessage(text='/pong')
    )
