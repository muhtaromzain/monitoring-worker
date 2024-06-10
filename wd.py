import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
from handler.MyHandler import MyHandler
import os

class WD():
    def watch():
        # path = os.path.join(os.sep, "input")
        path = "./input"
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        
        # path = sys.argv[1] if len(sys.argv) > 1 else '.'
        
        event_handler = MyHandler()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        
        try:
            while True:
                logging.info('Watching...')
                time.sleep(2)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        