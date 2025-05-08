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
# subscribe filter must be bytes
sock.setsockopt(zmq.SUBSCRIBE, b"json-full-miner_data")

while True:
    # recv_multipart() may return [payload] or [topic, payload]
    parts = sock.recv_multipart()
    print(parts)
    if len(parts) == 2:
        topic_frame, payload_frame = parts
    else:
        # single-frame case: it's already the payload
        topic_frame    = None
        payload_frame  = parts[0]

    # decode and parse
    try:
        message = json.loads(payload_frame.decode('utf-8'))
    except json.JSONDecodeError:
        # skip non-JSON frames
        continue

    # Optional: check topic if you care
    if topic_frame:
        topic = topic_frame.decode('utf-8')
        if topic != "json-full-miner_data":
            continue

    # Now you have the JSON in `message`
    height     = message["height"]
    prev_id    = message["prev_id"]
    difficulty = int(message["difficulty"], 16)
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
