"""Module for a thread-safe hash-map"""

from threading import Lock


class ConcurrentHashMap:
    """
    A thread-safe dictionary (hash-map).
    It uses a private mutex for accessing resources concurrently
    """
    def __init__(self):
        self._lock = Lock()
        self.dictionary = {}

    def add(self, key, value):
        """Add a 'key->value' entry in the dictionary"""
        with self._lock:
            self.dictionary[key] = value

    def get(self, key):
        """
        Is given a 'key' and returns its corresponding 'value'.
        Or None, if the dictionary doesn't contain it
        """
        with self._lock:
            return self.dictionary.get(key, None)

    def delete(self, key):
        """Remove a 'key' from the dictionary"""
        with self._lock:
            self.dictionary.pop(key)

    def contains(self, key) -> bool:
        """Returns whether or not the dictionary contains a given key"""
        with self._lock:
            return key in self.dictionary
