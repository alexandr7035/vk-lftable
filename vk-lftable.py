#!./venv/bin/python3
import flask

import sys
print(sys.argv)



app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return('Hello from Flask!')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
