# coding=utf-8
"""
CLI stub gen
"""
import argparse

from fluentogram.typing_generator import ParsedRawFTL, Tree, Stubs


def cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-ftl", dest="ftl_path", required=True)
    parser.add_argument("-stub", dest="stub_path", required=False)

    args = parser.parse_args()

    with open(args.ftl_path, "r", encoding="utf-8") as input_f:
        raw = ParsedRawFTL(input_f.read())

    tree = Tree(raw.get_messages())
    stubs = Stubs(tree)
    if args.stub_path:
        stubs.to_file(args.stub_path)
    else:
        print(stubs.echo())
