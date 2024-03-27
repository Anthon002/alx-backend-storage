#!/usr/bin/env python3
''' module for using redis
'''
import redis
import uuid
from functools import wraps
from typing import Callable, Union, Any


def count_calls(method: Callable) -> Callable:
    '''method to track number of calls
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''method to invoke after incrementing
        '''
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
            a_ = method(self, *args, **kwargs)
        return a_
    return invoker


def call_history(method: Callable) -> Callable:
    '''Tracks the call details of a method in a Cache class.
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''Returns the method's output after storing its inputs and output.
        '''
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    '''Displays the call history of a Cache class' method.
    '''
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


class Cache:
    '''This class represents data storage object in redis
    '''
    def __init__(self) -> None:
        ''' intializatin method
        '''
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''method to store value in redis
        '''
        key_ = str(uuid.uuid4())
        self._redis.set(key_, data)
        return key_

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        '''method to retrieve a value from the redis storage
        '''
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        '''method to retrieve str value from redis storage
        '''
        str_val = self.get(key, lambda x: x.decode('utf-8'))
        return str_val

    def get_int(self, key: str) -> int:
        '''method to retrieve in values from redis storage
        '''
        int_val = self.get(key, lambda x: int(x))
        return int_val
