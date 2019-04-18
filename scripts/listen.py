import asyncio
import websockets
import sys

async def listen(url, id):
    uri = 'ws://%s/attachSession/%s' % (url.split("://")[1],id)
    async with websockets.connect(uri) as websocket:
        done = False
        while not done:
          try:
              msg = await websocket.recv()
              print("> {}".format(msg))
          except ConnectionClosed:
              done = True

asyncio.get_event_loop().run_until_complete(listen(sys.argv[1],sys.argv[2]))