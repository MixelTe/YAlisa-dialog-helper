from flask import Flask, request
from dialog import Dialog
from YAlisa_dialog_helper import DialogManager
import json
import logging

logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
app = Flask(__name__)
dialogManager = DialogManager(Dialog)


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = dialogManager.handle_dialog(request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)

