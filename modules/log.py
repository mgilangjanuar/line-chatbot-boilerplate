from linebot.models import TextSendMessage
from lib import StandardClient
from model import Log


client = StandardClient(__name__)

@client.on_command()
def action_logging():
    """Save message to MongoDB
    """
    message = client.event.message
    Log(message_id=message.id, text=message.text).save()
