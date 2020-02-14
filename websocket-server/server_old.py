import asyncio
import json
import os

import websockets
import aioredis

redis_pool = None
redis_sub = None
redis_sub_channel = None
#redis_address = 'redis://localhost:0'  # TODO
redis_addres = os.environ.get('REDIS_PUBSUB_ADDRESS', 'redis://localhost')

CHANNEL = os.environ.get('WEBSOCKET_DEVICES_NOTIFICATION_RKEY', 'websocket-devices-notification')

active_websockets = set()


async def redis_connect():
    global redis_pool, redis_sub, redis_sub_channel
    redis_pool = await aioredis.create_redis_pool(
        redis_addres,
        minsize=5, maxsize=10)
    redis_sub = await aioredis.create_redis(redis_addres)
    sub = await redis_sub.subscribe(CHANNEL)
    print("subscribed {}".format(CHANNEL))
    redis_sub_channel = sub[0]


async def input_handler(websocket):  # unused: we don't receive from websocket (yet)

    print("start input handler..")
    async for message in websocket:
        print("## INPUT HNDLR: {}".format(message))


async def notification_handler(websocket):
    while True:
        print("start notification handler..")
        while await redis_sub_channel.wait_message():
            message = await redis_sub_channel.get()
            print("## NOTIF HNDLR: {}".format(message))
            await websocket.send(json.dumps(message.decode("utf-8")))
            print("sent!")



async def ws_handler(websocket, path):
    print("ws_handler..({})".format(path))
    active_websockets.add(websocket)
    try:
        # tasks = [asyncio.ensure_future(input_handler(websocket)),
        #          asyncio.ensure_future(notification_handler(websocket))]
        tasks = [asyncio.ensure_future(notification_handler(websocket))]
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.ALL_COMPLETED)
        for task in pending:
            task.cancel()
    finally:
        active_websockets.remove(websocket)


async def main():
    print("connect redis..")
    await redis_connect()
    print("..connected")
    ws_server = websockets.serve(ws_handler, '0.0.0.0', 5678)
    asyncio.ensure_future(ws_server)

#https://stackoverflow.com/questions/53689602/python-3-websockets-server-http-server-run-forever-serve-forever
#https://github.com/aaugustin/websockets/issues/116

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = asyncio.ensure_future(main())
    loop.run_until_complete(server)
    loop.run_forever()
