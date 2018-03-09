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


connect('poc_chatbot_boilerplate', host='localhost', port=27017, username=None, password=None)

app = Flask(__name__)
bot_handler = ChatbotHandler(load_clients, redis=redis.StrictRedis(host='localhost', port=6379, db=0))


@app.route('/service/chatbot/callback', methods=['POST'])
def route_service_chatbot_callback():
    try:
        bot_handler.handle(request, app.logger)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


if __name__ == '__main__':
    app.run()
