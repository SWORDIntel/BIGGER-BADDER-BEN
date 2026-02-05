use notify::{Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::{Path, PathBuf};
use std::sync::mpsc;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use tokio::time::sleep;

type Callback = Box<dyn Fn() + Send + Sync>;

pub struct ConfigWatcher {
    config_path: PathBuf,
    callback: Arc<Callback>,
    watcher: Option<RecommendedWatcher>,
    running: Arc<Mutex<bool>>,
}

impl ConfigWatcher {
    pub fn new<P: AsRef<Path>, F>(config_path: P, callback: F) -> Result<Self, Box<dyn std::error::Error>>
    where
        F: Fn() + Send + Sync + 'static,
    {
        let config_path = config_path.as_ref().to_path_buf();
        let callback: Arc<Callback> = Arc::new(Box::new(callback));
        let running = Arc::new(Mutex::new(false));
        
        Ok(Self {
            config_path,
            callback,
            watcher: None,
            running,
        })
    }
    
    pub fn start(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let (tx, rx) = mpsc::channel::<()>();
        let callback = Arc::clone(&self.callback);
        let config_path = self.config_path.clone();
        
        let mut watcher = RecommendedWatcher::new(
            move |res: Result<Event, notify::Error>| {
                match res {
                    Ok(event) => {
                        if matches!(event.kind, EventKind::Modify(_)) {
                            // Small delay to ensure file write is complete
                            thread::sleep(Duration::from_millis(100));
                            
                            // Verify file still exists and was actually modified
                            if config_path.exists() {
                                callback();
                            }
                        }
                    }
                    Err(e) => eprintln!("watch error: {:?}", e),
                }
            },
            Config::default(),
        )?;
        
        watcher.watch(&self.config_path, RecursiveMode::NonRecursive)?;
        self.watcher = Some(watcher);
        
        *self.running.lock().unwrap() = true;
        Ok(())
    }
    
    pub fn stop(&mut self) {
        if let Some(ref mut watcher) = self.watcher {
            let _ = watcher.unwatch(&self.config_path);
        }
        *self.running.lock().unwrap() = false;
    }
    
    pub fn is_running(&self) -> bool {
        *self.running.lock().unwrap()
    }
}

pub struct MultiConfigWatcher {
    watchers: Vec<ConfigWatcher>,
    running: Arc<Mutex<bool>>,
}

impl MultiConfigWatcher {
    pub fn new() -> Self {
        Self {
            watchers: Vec::new(),
            running: Arc::new(Mutex::new(false)),
        }
    }
    
    pub fn add_config<P: AsRef<Path>, F>(&mut self, config_path: P, callback: F) -> Result<(), Box<dyn std::error::Error>>
    where
        F: Fn() + Send + Sync + 'static,
    {
        let mut watcher = ConfigWatcher::new(config_path, callback)?;
        
        if *self.running.lock().unwrap() {
            watcher.start()?;
        }
        
        self.watchers.push(watcher);
        Ok(())
    }
    
    pub fn start(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        for watcher in &mut self.watchers {
            watcher.start()?;
        }
        *self.running.lock().unwrap() = true;
        Ok(())
    }
    
    pub fn stop(&mut self) {
        for watcher in &mut self.watchers {
            watcher.stop();
        }
        *self.running.lock().unwrap() = false;
    }
    
    pub fn is_running(&self) -> bool {
        *self.running.lock().unwrap()
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    
    if args.len() < 2 {
        eprintln!("Usage: {} <config_file>", args[0]);
        std::process::exit(1);
    }
    
    let config_path = &args[1];
    
    let mut watcher = ConfigWatcher::new(config_path, || {
        println!("Configuration file changed!");
    })?;
    
    println!("Watching {} for changes...", config_path);
    println!("Press Ctrl+C to stop");
    
    watcher.start()?;
    
    // Wait for interrupt
    loop {
        sleep(Duration::from_secs(1)).await;
    }
}
