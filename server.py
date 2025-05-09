import asyncio
import json

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    line = await reader.readline()      # reads until '\n'
    request = json.loads(line)
    # handle subscribe/authorize/notify…
    writer.write((json.dumps(response) + '\n').encode())
    await writer.drain()

async def main():
    server = await asyncio.start_server(handle, '0.0.0.0', 4545)
    await server.serve_forever()

asyncio.run(main())
