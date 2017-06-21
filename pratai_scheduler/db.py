# -*- coding: utf-8 -*-

"""
scheduler.db
~~~~~~~~~~~~
This module allows the scheduler to announce the joining and leaving of the
cluster.
"""

import logging

from elasticsearch import Elasticsearch
from elasticsearch import TransportError

from log import prepare_log
from config import parse_config

prepare_log()
logging.getLogger('pratai-scheduler')

HOSTS_ENDPOINT = parse_config("db")['hosts']
ES = Elasticsearch(hosts=HOSTS_ENDPOINT)


def get_image(function_id: str) -> dict:
    """Get a single function document from the db."""
    try:
        return ES.get(index='pratai', doc_type='function', id=function_id)
    except TransportError as error:
        logging.error(error)
        raise


def save_result(json_doc: dict) -> str:
    """Save the result of a function plus metadata"""
    try:
        res = ES.index(index='pratai', doc_type='response', body=json_doc)
        res.indices.refresh(index='pratai')
    except TransportError as error:
        logging.error(error)
        raise
    return res['created']
