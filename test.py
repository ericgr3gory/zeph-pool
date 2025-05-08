import zmq
import json
import requests

# Constants
ZMQ_ENDPOINT = "tcp://192.168.0.200:18083"
RPC_URL      = "http://10.66.66.2:18085/json_rpc"
POOL_ADDRESS = "ZEPHYR37Nih5NeNGLgKFMMfRVEPsaRDh1b9nkqcjjPen3G8RZVPaVtvc3gGELTC9geVsuquZogrSHCaP3sHvq8N6cyCSRJvkbUV57"
POOL_ID      = 1
RESERVE_SIZE = 8

ctx  = zmq.Context()
sock = ctx.socket(zmq.SUB)
sock.connect(ZMQ_ENDPOINT)
sock.setsockopt_string(zmq.SUBSCRIBE, "json-full-miner_data")

while True:
    message = sock.recv_string()
    if ':' in message:
        topic, payload = message.split(':', 1)
        if topic == "json-full-miner_data":
            try:
                data = json.loads(payload)
                height     = data["height"]
                prev_id    = data["prev_id"]
                difficulty = int(data["difficulty"], 16)
                print(f"ZMQ update — height {height}, difficulty {difficulty}")

                # Fetch the full template via RPC
                rpc_payload = {
                    "jsonrpc":"2.0", "id":"0",
                    "method":"get_block_template",
                    "params":{
                        "wallet_address": POOL_ADDRESS,
                        "reserve_size":   RESERVE_SIZE
                    }
                }
                tpl = requests.post(RPC_URL, json=rpc_payload).json()["result"]

                # Build job blob
                blob = bytearray.fromhex(tpl["blocktemplate_blob"])
                extranonce = POOL_ID.to_bytes(RESERVE_SIZE, 'little')
                offset     = tpl["reserved_offset"]
                blob[offset:offset+RESERVE_SIZE] = extranonce

                job = {
                    "blob":       blob.hex(),
                    "difficulty": tpl["difficulty"],
                    "height":     tpl["height"]
                }
                print("New job:", job)
            except json.JSONDecodeError:
                continue
