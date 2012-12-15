#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Store for saving a session in gae
'''

import datetime
import web.session
from google.appengine.ext import db

class Session(db.Model):
    data = db.TextProperty()
    atime = db.DateTimeProperty()

class DataStore(web.session.Store):
    '''
    Store for saving a session in gae Datastore
    '''

    def __init__(self, ancestor_key='session'):
        self.ancestor_key = ancestor_key
        key = db.Key.from_path('Session', self.ancestor_key)
        self.ancestor = db.get(key)
        if not self.ancestor:
            self.ancestor = Session(key_name=self.ancestor_key)
            self.ancestor.put()

    def __contains__(self, key):
        q = Session.all(keys_only=True)
        q.ancestor(self.ancestor)
        key = db.Key.from_path('Session', self.ancestor_key, 'Session', key)
        q.filter('__key__ =', key)
        return q.get() != None

    def __getitem__(self, key):
        key = db.Key.from_path('Session', self.ancestor_key, 'Session', key)
        s = db.get(key)
        s.atime = datetime.datetime.now()
        s.put()
        return self.decode(s.data)

    def __setitem__(self, key, value):
        s = Session(parent=self.ancestor, key_name=key)
        s.data = self.encode(value)
        s.atime = datetime.datetime.now()
        s.put()

    def __delitem__(self, key):
        key = db.Key.from_path('Session', self.ancestor_key, 'Session', key)
        db.delete(key)
    
    def cleanup(self, timeout):
        now = datetime.datetime.now()
        td = datetime.timedelta(seconds=timeout)
        time = now - td
        q = Session.all(keys_only=True)
        q.ancestor(self.ancestor)
        q.filter('atime <', time)
        keys = q.run()
        db.delete(keys)

class MemcacheStore(web.session.Store):
    '''
    Store for saving a session in gae memcache
    '''

    def __init__(self, prefix='session.', 
            timeout=web.config.session_parameters['timeout']):
        from google.appengine.api import memcache
        self.mc = memcache.Client()
        self.prefix = prefix
        self.timeout = timeout

    def __contains__(self, key):
        key = self.prefix + key
        return self.mc.get(key) != None

    def __getitem__(self, key):
        key = self.prefix + key
        value = self.mc.get(key)
        value = self.decode(value)
        return value

    def __setitem__(self, key, value):
        key = self.prefix + key
        value = self.encode(value)
        self.mc.set(key, value, self.timeout)

    def __delitem__(self, key):
        key = self.prefix + key
        self.mc.delete(key)
    
    def cleanup(self, timeout):
        pass
