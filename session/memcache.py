#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Store for saving a session in memcache
'''

import web.session

class MemcacheStore(web.session.Store):
    '''
    Store for saving a session in memcache
    '''

    def __init__(self, mc, prefix='session.', 
            timeout=web.config.session_parameters['timeout']):
        self.mc = mc
        self.prefix = prefix
        self.timeout = timeout

    def __contains__(self, key):
        key = self._prepare_key(key)
        return self.mc.append(key, '')

    def __getitem__(self, key):
        key = self._prepare_key(key)
        return self.mc.get(key)

    def __setitem__(self, key, value):
        key = self._prepare_key(key)
        self.mc.set(key, value, self.timeout)

    def __delitem__(self, key):
        key = self._prepare_key(key)
        self.mc.delete(key)
    
    def cleanup(self, timeout):
        pass

    def _prepare_key(self, key):
        return self.prefix + key
