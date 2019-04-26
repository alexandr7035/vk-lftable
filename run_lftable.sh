#!/bin/sh

ADDR='127.0.0.1'
PORT='8080'
VENV_DIR='venv'
DEP_FILE='requirements.txt'

if [ ! -d $VENV_DIR ]
then
	echo "- Creating a virtual environment..."
	python3 -m venv venv
	echo "- Installing dependencies from $DEP_FILE..."
	./venv/bin/pip3 -q install -r requirements.txt
fi

echo "- Starting vk-lftable..."
./venv/bin/gunicorn vk-lftable:app --bind $ADDR:$PORT
