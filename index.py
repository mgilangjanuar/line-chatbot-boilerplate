from flask import (
    Flask,
    request,
    abort
)
from linebot.exceptions import InvalidSignatureError
from register import load_clients
from lib import ChatbotHandler


app = Flask(__name__)
bot_handler = ChatbotHandler(load_clients)


@app.route('/service/chatbot/callback', methods=['POST'])
def route_service_chatbot_callback():
    try:
        bot_handler.handle(request, app.logger)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


if __name__ == '__main__':
    app.run()
