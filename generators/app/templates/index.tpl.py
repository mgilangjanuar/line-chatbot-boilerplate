import redis
from flask import (
    Flask,
    request,
    abort
)
from linebot.exceptions import InvalidSignatureError
from register import load_clients
from lib import ChatbotHandler
<%= importMongoengine %>


<%= createMongoConnection %>

my_redis    = <%= redisConfiguration %>
bot_handler = ChatbotHandler(load_clients, redis=my_redis)
app         = Flask(__name__)


@app.route('<%= routeCallback %>', methods=['POST'])
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
