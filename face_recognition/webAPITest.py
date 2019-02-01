import json
import time
from ws4py.client.threadedclient import WebSocketClient
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QSplashScreen, QPixmap, Qt
import face
import _thread
import window

class CG_Client(WebSocketClient):

    def opened(self):
        req = '{"event":"subscribe", "channel":"eth_usdt.deep"}'
        #req = '{"req": "topic to req","id": "id generate by client"}'
        self.send(req)



    def closed(self, code, reason=None):
        print("Closed down:", code, reason)

    def received_message(self, resp):
        resp = json.loads(str(resp))
        data = resp['data']
        if type(data) is dict:
            for a in data:
                print(time.time())
                window.window(str(time.time()))

            #ask = data['asks'][0]
            #print('Ask:', ask)
            #bid = data['bids'][0]
            #print('Bid:', bid)





if __name__ == '__main__':
    ws = None
    try:
        ws = CG_Client('wss://i.cg.net/wi/ws')
        #ws = CG_Client('wss://api.hadax.com/ws')
        ws.connect()
        ws.run_forever()

    except KeyboardInterrupt:
        ws.close()
