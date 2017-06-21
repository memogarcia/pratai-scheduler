# -*- coding: utf-8 -*-

"""
scheduler.sender_receiver
~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a sender and a receiver that will listen to event
producers and send the tasks to the pratai nodes.
"""

import asyncio
import uvloop

import logging
import uuid

import zmq

from config import parse_config
import db
import cluster

from log import prepare_log

prepare_log()
logging.getLogger('pratai-scheduler')


async def scheduler() -> None:
    """Scheduler

    This loop will listen for messages from the event sources like
    the api, the agent and 3rd party ones.

    Once a new message arrives it will write it to the node queues for further
    processing.
    """
    context = zmq.Context()

    receiver = context.socket(zmq.PULL)
    receiver_endpoint = parse_config("queue")['receiver_endpoint']
    receiver.bind(receiver_endpoint)

    sender = context.socket(zmq.PUSH)
    sender_endpoint = parse_config("queue")['sender_endpoint']
    sender.bind(sender_endpoint)

    daemon_id = uuid.uuid4().hex
    scheduler_id = cluster.join(daemon_id, 'scheduler')
    print('Scheduler {} running...'.format(daemon_id))

    try:
        while True:
            work = receiver.recv_json()

            image = await db.get_image(work['function_id'])
            work['image_id'] = image.image_id

            logging.info('Processing function {} for request {}'.format(
                work['function_id'], work['request_id']))

            await sender.send_json(work)

    except (KeyboardInterrupt, Exception) as error:
        logging.error(error)

    finally:
        receiver.close()
        sender.close()
        cluster.leave(daemon_id)


if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    future = asyncio.ensure_future(scheduler())
    loop.run_until_complete(future)
    loop.close()
