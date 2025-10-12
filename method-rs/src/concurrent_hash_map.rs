use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub struct ConcurrentHashMap<K, V> {
    hash_map: Arc<Mutex<HashMap<K, V>>>,
}

impl<K, V> ConcurrentHashMap<K, V>
where
    K: std::cmp::Eq + std::hash::Hash + Clone,
    V: Clone,
{
    pub fn new() -> Self {
        Self {
            hash_map: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn contains(&self, key: &K) -> bool {
        let map = self.hash_map.lock().unwrap();
        map.contains_key(key)
    }

    pub fn insert(&self, key: K, value: V) {
        let mut map = self.hash_map.lock().unwrap();
        map.insert(key, value);
    }

    pub fn delete(&self, key: &K) {
        let mut map = self.hash_map.lock().unwrap();
        map.remove(key);
    }

    /// Clone a reference (so threads can share ownership)
    pub fn clone_ref(&self) -> Self {
        Self {
            hash_map: Arc::clone(&self.hash_map),
        }
    }

    /// Get a value's copy
    pub fn get(&self, key: &K) -> Option<V> {
        let map = self.hash_map.lock().unwrap();
        map.get(key).cloned()
    }
}
