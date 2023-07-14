from flask import Flask, request, abort
import timepad
import time
from timepad.rest import ApiException
#from timepad.configuration import Configuration
from timepad import rest, configuration, Api, api_client, api
from timepad.api import DefaultApi
from timepad.configuration import Configuration
from timepad.api_client import ApiClient

configuration1 = Configuration()
configuration1.access_token = 'c08ef390e759340fc86bd903ca8906894b59b1a4'

api_instance = DefaultApi(ApiClient(configuration1))


app = Flask(__name__)



@app.route('/', methods = ['POST'])
def webhook():
    if request.method == 'POST':
        json_request = request.json
        try:
            if json_request["status_raw"] == 'pending':
                str_order_id = json_request["order_id"]
                event_id = json_request["event_id"]
                api_instance.approve_event_order(event_id, int(str_order_id))
            return ('success', 200)
        except ApiException as e:
            print("Exception when calling DefaultApi->approve_event_order: %s\n" % e)
            abort(400)
    else:
        abort(400)

if __name__ == '__main__':
    app.run()