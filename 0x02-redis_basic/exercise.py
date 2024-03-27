#!/usr/bin/env python3
''' module for using redis
'''
import redis
from typing import Callable, Union, Any
from functools import wraps
import uuid


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
    '''method to keep track of details of calls for a method 
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''method to return the output
        '''
        _key_in_ = '{}:inputs'.format(method.__qualname__)
        _key_out_ = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(_key_in_, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(_key_out_, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    '''method to display call history 
    '''
    if fn is None or not hasattr(fn, '__self__'):
        return
    _store_redis = getattr(fn.__self__, '_redis', None)
    if not isinstance(_store_redis, redis.Redis):
        return
    _name_func = fn.__qualname__
    _key_in_ = '{}:inputs'.format(_name_func)
    _key_out_ = '{}:outputs'.format(_name_func)
    fxn_call_count = 0
    if _store_redis.exists(_name_func) != 0:
        fxn_call_count = int(_store_redis.get(_name_func))
    print('{} was called {} times:'.format(_name_func, fxn_call_count))
    _input_func = _store_redis.lrange(_key_in_, 0, -1)
    _output_func = _store_redis.lrange(_key_out_, 0, -1)
    for fxn_input, fxn_output in zip(_input_func, _output_func):
        print('{}(*{}) -> {}'.format(
            _name_func,
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
        _a = fn(data) if fn is not None else data
        return _a

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
