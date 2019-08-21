import flask
import src.bot

bot = src.bot.LFTableBot()

app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def main_handler():
    return(bot.handle_request(flask.request))
