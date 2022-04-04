# coding=utf-8
"""
CLI stub gen
"""
import argparse

from .ftl_to_stub import ftl_to_stub


def cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-ftl", dest="ftl_path", required=True)
    parser.add_argument("-stub", dest="stub_path", required=True)

    args = parser.parse_args()

    code = ftl_to_stub(ftl_path=args.ftl_path)
    with open(args.stub_path, "wt", encoding="utf-8") as f:
        f.write(code)
