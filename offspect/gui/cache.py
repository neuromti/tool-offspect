# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from cachetools import cached, LRUCache

def load_files(self):
    path = self.file_path_line.text()
    pass

cache = LRUCache(maxsize=32) # least recently used, with size specified
lock  = RLock() # potentially needed for synchronizing thread access to the cache

@cached(cache, lock=lock) # cache decorator
def cache_files(self):
    pass