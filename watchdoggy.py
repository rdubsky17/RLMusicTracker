import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import spotify_logger
import StatReader

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            
            spotify_logger.log_tracks("RLTracker\\spotify_log.csv", 50)
            currentStats = StatReader.getStats("Goku SSJGSS")
            currentStats.to_csv("RLTracker\\CurrentStats.csv")
        
if __name__ == "__main__":
    folder_to_watch = "RLTracker\\GameStats"  

    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()

    print(f"Watching folder: {folder_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()