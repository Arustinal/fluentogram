import argparse
import time
from pathlib import Path

from watchdog.events import FileModifiedEvent
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from fluentogram.typing_generator import ParsedRawFTL, Stubs, Tree


class FtlFileEventHandler(FileSystemEventHandler):
    def __init__(self, track_path: str, stub_path: str):
        self.track_path = track_path
        self.stub_path = stub_path

    def on_modified(self, event: FileModifiedEvent):
        print('event type: %s, path: %s' % (event.event_type, event.src_path))
        if not event.is_directory:
            messages = parse_ftl_dir(self.track_path)
            tree = Tree(messages)
            stubs = Stubs(tree)
            stubs.to_file(self.stub_path)


def parse_ftl(ftl_path: str | Path) -> dict:
    with open(ftl_path, "r", encoding="utf-8") as input_f:
        raw = ParsedRawFTL(input_f.read())
    messages = raw.get_messages()
    return messages


def parse_ftl_dir(dir_path: str) -> dict:
    messages = {}
    for file in Path(dir_path).glob("*.ftl"):
        messages.update(parse_ftl(file))
    return messages


def watch_ftl_dir(track_path: str, stub_path: str) -> None:
    observer = Observer()
    observer.schedule(FtlFileEventHandler(track_path, stub_path), track_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


def cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-ftl", dest="ftl_path", required=False)
    parser.add_argument("-track-ftl", dest="track_path", required=False)
    parser.add_argument("-dir-ftl", dest="dir_path", required=False)
    parser.add_argument("-stub", dest="stub_path", required=False)

    args = parser.parse_args()

    if not args.ftl_path and not args.track_path and not args.dir_path:
        print("Use 'i18n --help' to see help message")
        return

    if args.track_path:
        print("Watching for changes in %s" % args.track_path)
        watch_ftl_dir(args.track_path, args.stub_path)
        return

    elif args.dir_path:
        messages = parse_ftl_dir(args.dir_path)
    else:
        messages = parse_ftl(args.ftl_path)

    tree = Tree(messages)
    stubs = Stubs(tree)
    if args.stub_path:
        stubs.to_file(args.stub_path)
    else:
        print(stubs.echo())
