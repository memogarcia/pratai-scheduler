# -*- coding: utf-8 -*-

"""
scheduler.collector
~~~~~~~~~~~~~~~~~~~
This module contains a collector who's listening to function responses.
"""

import asyncio
import uvloop

import logging
import uuid

import zmq

from config import parse_config
import cluster
import db

from log import prepare_log

prepare_log()
logging.getLogger('pratai-scheduler')


async def collector() -> None:
    """Collector

    This loop will listen for messages coming from the nodes as responses from
    functions.

    Once a new message arrives it will get stored in the database and/or
    re-scheduled for further processing.
    """
    context = zmq.Context()

    responses = context.socket(zmq.PULL)

    collector_endpoint = parse_config("queue")['collector_endpoint']
    responses.connect(collector_endpoint)

    daemon_id = uuid.uuid4().hex
    collector_id = cluster.join(daemon_id, 'collector')
    print('Collector {} running...'.format(daemon_id))

    try:

        while True:
            result = responses.recv_json()
            await db.save_result(result)

            logging.info('Saved result for function {} with request {}'.format(
                result['function_id'], result['request_id']))

    except (KeyboardInterrupt, Exception) as error:
        logging.error(error)

    finally:
        responses.close()
        cluster.leave(daemon_id)


if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    future = asyncio.ensure_future(collector())
    loop.run_until_complete(future)
    loop.close()
