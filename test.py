import zmq
import json
import requests

# Define your pool address
POOL_ADDRESS = "ZEPHYR37Nih5NeNGLgKFMMfRVEPsaRDh1b9nkqcjjPen3G8RZVPaVtvc3gGELTC9geVsuquZogrSHCaP3sHvq8N6cyCSRJvkbUV57"

# 1. Initialize ZMQ SUB socket
context = zmq.Context()
socket  = context.socket(zmq.SUB)
socket.connect("tcp://192.168.0.200:18083")       # ZMQ publisher endpoint
socket.setsockopt(zmq.SUBSCRIBE, b"json-full-miner_data")  # subscribe to topic

while True:
    # 2. Receive multipart message: topic and payload
    topic_frame, payload_frame = socket.recv_multipart()      # :contentReference[oaicite:7]{index=7}
    topic   = topic_frame.decode()                            # decode topic
    message = json.loads(payload_frame.decode())              # parse JSON

    # 3. Extract header info
    height     = message["height"]
    prev_id    = message["prev_id"]
    difficulty = int(message["difficulty"], 16)

    # 4. Fetch full template via RPC
    rpc_payload = {
        "jsonrpc": "2.0",
        "id":      "0",
        "method":  "get_block_template",
        "params": {
            "wallet_address": POOL_ADDRESS,
            "reserve_size":   8
        }
    }
    rpc_url = "http://10.66.66.2:18085/json_rpc"
    tpl = requests.post(rpc_url, json=rpc_payload).json()["result"]

    # 5. Inject extranonce into the mutable blob
    blob_hex        = tpl["blocktemplate_blob"]
    reserved_offset = tpl["reserved_offset"]
    blob            = bytearray.fromhex(blob_hex)

    pool_id    = 1
    extranonce = pool_id.to_bytes(8, 'little')
    blob[reserved_offset:reserved_offset+8] = extranonce    # overwrite reserved bytes

    # 6. Publish job to miners
    job = {
        "blob":       blob.hex(),
        "difficulty": tpl["difficulty"],
        "height":     tpl["height"],
    }
    print("New job:", job)

    # Throttle if needed
    # time.sleep(0.1)
