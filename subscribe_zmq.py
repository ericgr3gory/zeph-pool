import zmq
import json
import requests

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://192.168.0.200:18083")
socket.setsockopt_string(zmq.SUBSCRIBE, "json-full-miner_data")

while True:
    raw = socket.recv_multipart()
    message = raw[0].decode('utf-8')
    data = json.loads(message)
    print(data)
    height, prev_id = message["height"], message["prev_id"]
    difficulty = int(message["difficulty"], 16)
    print(difficulty)
        
    ''''
        data = {
                "jsonrpc":"2.0","id":"0","method":"getblocktemplate","params":{"wallet_address":POOL_ADDRESS}
                }
        tpl = requests.post("http://10.66.66.2:18085/json_rpc", json=data).json()["result"]
        blob = tpl["blocktemplate_blob"]
        reserved_offset = tpl["reserved_offset"]
        '''
