#!./venv/bin/python3 -B
import flask

from flask import Flask, request, json
import vk


import sys
import vk
print(sys.argv)

vk_api_version = 5.90

# Токены
try:
    from tokens import vk_token
except Exception:
    print("Can't load vk_token from file. Exit.")

try:
    from tokens import confirmation_token
except Exception:
    print("Can't load confirmation_token from file. Exit.")



def menu_keyboard():
	
	
	
    keyb = {
    "one_time": False,
    "buttons": [
      [{
        "action": {
          "type": "text",
          "payload": "{\"button\": \"1\"}",
          "label": "Red"
        },
        "color": "negative"
      },
     {
        "action": {
          "type": "text",
          "payload": "{\"button\": \"2\"}",
          "label": "Green"
        },
        "color": "positive"
      }],
      [{
        "action": {
          "type": "text",
          "payload": "{\"button\": \"3\"}",
          "label": "White"
        },
        "color": "default"
      },
     {
        "action": {
          "type": "text",
          "payload": "{\"button\": \"4\"}",
          "label": "Blue"
        },
        "color": "primary"
      }]
    ]
  }

    return(json.dumps(keyb))






app = flask.Flask(__name__)


@app.route('/', methods=['POST'])
def processing():

    data = json.loads(request.data)
    print(data)

    if 'type' not in data.keys():
        return 'not vk'

    if data['type'] == 'confirmation':
        return confirmation_token

    elif data['type'] == 'message_new':
        session = vk.Session()
        api = vk.API(session, v=vk_api_version)

        # User who calls bot
        user_id = data['object']['from_id']

        api.messages.send(access_token=vk_token, user_id=str(user_id), message='Hello world!', keyboard=menu_keyboard())

        return 'ok'






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
