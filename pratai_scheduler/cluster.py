# -*- coding: utf-8 -*-

"""
scheduler.cluster
~~~~~~~~~~~~~~~~~
This module allows the scheduler to announce the joining and leaving of the
cluster.
"""
import logging

from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch import TransportError

from log import prepare_log
from config import parse_config

prepare_log()
logging.getLogger('pratai-scheduler')

HOSTS_ENDPOINT = parse_config("db")['hosts']
ES = Elasticsearch(hosts=HOSTS_ENDPOINT)


def join(daemon_id: str, daemon_type: str) -> str:
    """Join the scheduler to the cluster.
    """
    doc = {
        "daemon_type": daemon_type,
        "daemon_id": daemon_id,
        "joined_at": datetime.now(),
        "status": "running"
    }
    try:
        res = ES.index(index='pratai',
                       doc_type='daemon',
                       body=doc,
                       id=daemon_id)

        ES.indices.refresh(index='pratai')
    except TransportError as error:
        logging.error(error)
        raise
    return res['created']


def leave(daemon_id: str) -> dict:
    """Announce the scheduler is leaving.
    """
    try:
        return ES.delete(index='pratai', doc_type='daemon', id=daemon_id)
    except TransportError as error:
        logging.error(error)
        raise
