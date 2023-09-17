import time
import kopf

import common

import core

import handlers

logger = common.Logger(__name__)

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.execution.max_workers = 1