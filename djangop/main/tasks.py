from __future__ import absolute_import, unicode_literals

import datetime

import pytz

from djangop.celery import app
from main.models import SandboxMatch


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)


@app.task
def printSomething(thing):
    print(thing)


@app.task
def abort_unfinished_games():
    now = datetime.datetime.now()
    matches_to_abort = SandboxMatch.objects.filter(state=1)

    for match in matches_to_abort:
        max_match_length = 0
        if match.type is not None:
            max_match_length = match.type.max_match_length
        else:
            max_match_length = match.game.max_match_length

        abort_time = match.date_started + datetime.timedelta(minutes=max_match_length)
        now = pytz.utc.localize(now)

        if now >= abort_time:
            match.abort_match()

    return True
