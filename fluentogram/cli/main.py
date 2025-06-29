import argparse

from fluentogram.stub_generator.generator import generate


def cli() -> None:
    parser = argparse.ArgumentParser(prog="fluentogram")
    parser.add_argument("-o", dest="output_file", required=True)
    parser.add_argument("-f", dest="file_path", required=False)
    parser.add_argument("-d", dest="dir_path", required=False)

    args = parser.parse_args()
    if args.file_path is None and args.dir_path is None:
        raise ValueError("You must provide either a file or a directory")

    generate(args.output_file, args.file_path, args.dir_path)
