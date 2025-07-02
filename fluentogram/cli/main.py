from __future__ import annotations

import argparse
import time
from pathlib import Path

from watchdog.events import (
    FileModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from fluentogram.stub_generator.generator import generate


class FluentogramFileHandler(FileSystemEventHandler):
    """Handler for file system events that regenerates stubs when files change."""

    def __init__(self, output_file: str, file_path: str | None, dir_path: str | None) -> None:
        self.output_file = output_file
        self.file_path = file_path
        self.dir_path = dir_path

    def on_modified(self, event: FileModifiedEvent) -> None:
        print(f"event type: {event.event_type}, path: {event.src_path}")
        if not event.is_directory:
            generate(self.output_file, self.file_path, self.dir_path)
            print(f"Regenerated stubs for {event.src_path}")


def watch_files(output_file: str, file_path: str | None, dir_path: str | None) -> None:
    """Start watching files/directories for changes."""
    event_handler = FluentogramFileHandler(output_file, file_path, dir_path)
    observer = Observer()

    if file_path:
        # Watch specific file
        file_dir = str(Path(file_path).parent)
        observer.schedule(event_handler, file_dir, recursive=False)
        print(f"Watching file: {file_path}")
    elif dir_path:
        # Watch directory recursively
        observer.schedule(event_handler, dir_path, recursive=True)
        print(f"Watching directory: {dir_path}")

    observer.start()
    print("File watcher started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nFile watcher stopped.")

    observer.join()


def cli() -> None:
    parser = argparse.ArgumentParser(prog="fluentogram")
    parser.add_argument("-o", "--output-file", dest="output_file", required=False, help="Path to the output file")
    parser.add_argument("-f", "--file-path", dest="file_path", required=False, help="Path to the file to watch")
    parser.add_argument(
        "-w",
        "--watch",
        dest="watch",
        required=False,
        help="Watch for file changes and regenerate stubs automatically",
    )
    parser.add_argument("-d", "--dir-path", dest="dir_path", required=False, help="Path to the directory to watch")
    # back compatibility

    parser.add_argument("-ftl", dest="ftl_path", required=False, help="Path to the file to watch")
    parser.add_argument("-track-ftl", dest="watch", required=False, help="Path to the file to watch")
    parser.add_argument("-dir-ftl", dest="dir_path", required=False, help="Path to the directory to watch")
    parser.add_argument("-stub", dest="output_file", required=False, help="Path to the output file")

    args = parser.parse_args()

    if not args.output_file:
        args.output_file = "fluentogram.pyi"

    if args.watch:
        # Start watching for changes
        watch_files(args.output_file, args.file_path, args.dir_path)
    else:
        # Generate stubs once
        generate(args.output_file, args.file_path, args.dir_path)
