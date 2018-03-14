import redis
from flask import (
    Flask,
    request,
    abort
)
from linebot.exceptions import InvalidSignatureError
from mongoengine import connect
from register import load_clients
from lib import ChatbotHandler


# create connection to MongoDB
connect('poc_chatbot_boilerplate', host='localhost', port=27017, username=None, password=None)

# connect to Redis server
my_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

# define bot handler
bot_handler = ChatbotHandler(load_clients, redis=my_redis)

# initiate Flask app
app = Flask(__name__)


@app.route('/service/chatbot/callback', methods=['POST'])
def route_service_chatbot_callback():
    """
    This route for chatbot's webhook and magically 
    handle all requests
    """
    try:
        bot_handler.handle(request, app.logger)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


if __name__ == '__main__':
    app.run()
