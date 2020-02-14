#!/usr/bin/env python3
import json

import aiohttp
from aiohttp import web, WSCloseCode
import asyncio
import os

import aioredis

redis_pool = None
redis_sub = None
redis_sub_channel = None
redis_addres = os.environ.get('REDIS_PUBSUB_ADDRESS', 'redis://localhost')

CHANNEL = os.environ.get('WEBSOCKET_DEVICES_NOTIFICATION_RKEY', 'websocket-devices-notification')

async def redis_connect():
    global redis_pool, redis_sub, redis_sub_channel
    redis_pool = await aioredis.create_redis_pool(
        redis_addres,
        minsize=5, maxsize=10)
    redis_sub = await aioredis.create_redis(redis_addres)
    sub = await redis_sub.subscribe(CHANNEL)
    print("subscribed {}".format(CHANNEL))
    redis_sub_channel = sub[0]


async def http_handler(request):
    return web.Response(status=200, text="Working")

wss = []

async def redis_subscriber():
    print("websocket_redis_pubsub_handler started")
    while True:
        while await redis_sub_channel.wait_message():
            message = await redis_sub_channel.get()
            print("## NOTIF HNDLR: {}".format(message))
            wss[:] = [ws for ws in wss if not ws.closed]
            for ws in wss:
                await ws.send_str(json.dumps(message.decode("utf-8")))
                print("sent!")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("got client...")
    wss.append(ws)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str('some websocket message payload')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    return ws


def create_runner():
    app = web.Application()
    app.add_routes([
        web.get('/',   http_handler),
        #web.get('/ws', websocket_redis_pubsub_handler),
        web.get('/ws', websocket_handler),
    ])
    return web.AppRunner(app)


async def start_server(host="0.0.0.0", port=5678):
    print("connect redis..")
    await redis_connect()
    print("..connected")
    asyncio.create_task(redis_subscriber())
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()
