import asyncio

async def handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr!r}")
    while True:
        data = await reader.read(1024)            # up to 1 KiB
        if not data:
            print(f"Connection closed by {addr!r}")
            break
        message = data.decode()
        print(f"Received {message!r} from {addr!r}")
        writer.write(data)                         # echo back
        await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main(host='127.0.0.1', port=8888):
    server = await asyncio.start_server(handle_echo, host, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
