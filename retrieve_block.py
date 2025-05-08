import zmq
import json
import requests

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://192.168.0.200:18083")
socket.setsockopt_string(zmq.SUBSCRIBE, "json-full-miner_data")
POOL_ADDRESS = "ZEPHYR37Nih5NeNGLgKFMMfRVEPsaRDh1b9nkqcjjPen3G8RZVPaVtvc3gGELTC9geVsuquZogrSHCaP3sHvq8N6cyCSRJvkbUV57"
while True:
    try:
        parts = socket.recv_multipart()

        if parts:
            data = {
                        "jsonrpc": "2.0",
                        "id":      "0",
                        "method":  "get_block_template",
                        "params": {
                        "wallet_address": POOL_ADDRESS,
                        "reserve_size":   8
                                }
                        }       
            rpc_url = "http://10.66.66.2:18085/json_rpc"
            tpl = requests.post(rpc_url, json=data).json()["result"]

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


        if len(parts) == 1:
            message = parts[0].decode('utf-8')
            if ':' in message:
                topic, payload = message.split(":", 1)
            else:
                topic = "unknown"
                payload = message
        else:
            topic = parts[0].decode('utf-8')
            payload = parts[1].decode('utf-8')

        if topic == "json-full-miner_data":
            data = json.loads(payload)
            height = data.get("height")
            prev_id = data.get("prev_id")
            difficulty = int(data.get("difficulty"), 16)
            print(f"Height: {height}, Previous ID: {prev_id}, Difficulty: {difficulty}")
    except Exception as e:
        print(f"Error: {e}")
