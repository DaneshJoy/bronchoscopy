# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


class Singleton1(object):
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls, x, y):
        if cls._instance is None:
            # print('Creating new instance')
            cls._instance = cls.__new__(cls)
            # Put any initialization here (only the first is considered).
            # cls.x = x
            # cls.y = y
        # Put any initialization here (only the last is considered).
        cls.x = x
        cls.y = y
        return cls._instance
    
    def __str__(cls):
        return f'{repr(cls._instance)}: {cls._instance.x}, {cls._instance.y}'


class Singleton2(object):
    _instance = None

    def __new__(cls, x, y):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(Singleton2, cls).__new__(cls)
            # Put any initialization here (only the first is considered).
            cls.x = x
            cls.y = y
        # Put any initialization here (only the last is considered).
        # cls.x = x
        # cls.y = y
        return cls._instance
    
    def __str__(cls):
        return f'{repr(cls._instance)}: {cls._instance.x}, {cls._instance.y}'
         
         
s1 = Singleton1.instance(10,20)
s2 = Singleton1.instance(30,40)
print(s1)
print(s2)

s1 = Singleton2(10,20)
s2 = Singleton2(30,40)
print(s1)
print(s2)
