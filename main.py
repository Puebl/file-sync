import time
import shutil
from pathlib import Path
from configparser import ConfigParser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SyncHandler(FileSystemEventHandler):
    def __init__(self, src: Path, dst: Path):
        self.src = src
        self.dst = dst

    def _mirror(self, src_path: Path):
        rel = src_path.relative_to(self.src)
        dst_path = self.dst / rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)

    def _remove(self, src_path: Path):
        rel = src_path.relative_to(self.src)
        dst_path = self.dst / rel
        if dst_path.exists():
            if dst_path.is_file():
                dst_path.unlink(missing_ok=True)
            else:
                shutil.rmtree(dst_path, ignore_errors=True)

    def on_created(self, event):
        if not event.is_directory:
            self._mirror(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self._mirror(Path(event.src_path))

    def on_moved(self, event):
        # treat as delete+create
        self._remove(Path(event.src_path))
        if not event.is_directory:
            self._mirror(Path(event.dest_path))

    def on_deleted(self, event):
        self._remove(Path(event.src_path))


def main():
    cfg = ConfigParser()
    cfg.read('config.ini', encoding='utf-8')
    src = Path(cfg.get('source', 'path', fallback='')).expanduser()
    dst = Path(cfg.get('destination', 'path', fallback='')).expanduser()
    if not src or not dst:
        print('[ERR] Configure source/destination in config.ini')
        return
    if not src.exists():
        print(f'[ERR] Source not found: {src}')
        return
    dst.mkdir(parents=True, exist_ok=True)

    handler = SyncHandler(src, dst)
    obs = Observer()
    obs.schedule(handler, str(src), recursive=True)
    obs.start()
    print(f'[INFO] Watching {src} -> {dst}. Ctrl+C to stop.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        obs.stop()
        obs.join()

if __name__ == '__main__':
    main()
