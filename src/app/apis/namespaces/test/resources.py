import threading
import multiprocessing
from multiprocessing import Value
import time
import json
from datetime import datetime, timedelta
from flask_restplus import Resource, abort
from app import errors
from app.errors import BizError
from .api import api


@api.route('/')
class Test(Resource):
    def get(self):
        return dict(test='OK', ns='test', path='/'), 200, {'cs-api-xxx': json.dumps(dict(ns='test', path='/'))}


@api.route('/abort')
class TestAbort(Resource):
    def get(self):
        abort(400, 'test abort 400', custom=dict(ns='test', path='/abort'))


@api.route('/biz_error')
class TestBizError(Resource):
    def get(self):
        raise BizError(errors.ERR_XXX, 'what ever xxx', dict(ns='test', path='/biz_error'))


tlock = threading.RLock()


@api.route('/test_threads')
class TestThreads(Resource):
    def get(self):
        ret = False
        with tlock as lock:
            if lock:
                time.sleep(2)
                ret = True
        return dict(ret=ret, tident=threading.get_ident(), pident=multiprocessing.current_process().ident)


plock = multiprocessing.RLock()
pn = [0]
pln = Value('i', 0)


@api.route('/test_processes')
class TestProcesses(Resource):
    def get(self):
        n = datetime.utcnow()
        ret = False
        lock = plock.acquire(block=False)
        if lock:
            while True:
                if datetime.utcnow() - n > timedelta(seconds=2):
                    break
            # time.sleep(1)
            ret = True
            plock.release()
        pln.value += 1
        pn[0] += 1
        return dict(ret=ret, tident=threading.get_ident(), pident=multiprocessing.current_process().ident, pn=pn,
                    pln=pln.value)
