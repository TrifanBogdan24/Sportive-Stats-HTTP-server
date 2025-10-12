```
AppState
 ├── Table (protected by Mutex)
 └── JobManager
       └── Arc<ThreadPool>
             └── Worker threads...
```