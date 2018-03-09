from linebot.models import TextSendMessage
from lib import TextClient


client = TextClient(__name__)

@client.on_command('ping', sources=['user'])
def action_ping():
    """Always reply "/pong" when user type "/ping"
    """
    client.bot.reply_message(
        client.event.reply_token,
        TextSendMessage(text='/pong')
    )
