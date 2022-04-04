# coding=utf-8
"""Sorry about this bullshit."""
from typing import Dict, List

from fluent_compiler.bundle import FluentBundle
from fluent_compiler.resource import FtlResource


def ftl_to_stub(
        ftl_path: str,
        locale: str = "en-US",
        root_class_name: str = "TranslatorRunner") -> str:
    """Convert FTL file content to python stub file content.
    Pay attention to preventing FTL content like

    some-key = Sample text
    some-key-name = Sample text, name!

    Parser will raise error, because some-keys should be a common point, not a completed translation key by itself.
    Replace with:

    some-key-base = Sample text
    some-key-name = Sample text, name!
    """
    raw_items = _ftl_bundle_to_raw_items(ftl_path, locale=locale)
    nested_dict = _raw_items_to_nested_dict(raw_items)
    code = _nested_dict_to_stub(nested_dict, root_class_name=root_class_name)
    return code


def _ftl_bundle_to_raw_items(ftl_path: str, locale: str, **kwargs) -> Dict[str, str]:
    raw_ftl = FluentBundle(
        locale=locale, resources=[FtlResource.from_file(ftl_path)], **kwargs
    ).__dict__.get("_compiled_messages")
    if raw_ftl:
        raw_data: Dict[str, str] = {}
        for name, func in raw_ftl.items():
            raw_data.update({name: func([], []).replace("\n", "")})
        return raw_data
    else:
        raise ValueError("Empty/incorrect ftl file")


def _build_nested_dict(data: dict, items_iterator: iter, key: str, *rest: List[str]):
    """Turns flat structure of raw ftl items into a nested dictionary.It is recursive.Mutates the input dictionary!"""
    value = data.setdefault(key, {})
    if rest:
        _build_nested_dict(value, items_iterator, *rest)
    else:
        data[key] = next(items_iterator)


def _raw_items_to_nested_dict(items: dict, separator: str = "-") -> Dict:
    data = {}
    iterator = iter(items.values())

    for sequence, item in items.items():
        _build_nested_dict(data, iterator, *sequence.split(separator))
    return data


def soft_capitalize(string: str):
    """Capitalizes string without affecting other chars"""
    return f"{string[0].upper()}{string[1:]}"


def _recursive_build_stub(partial_data: dict) -> str:
    text = ""
    for key, value in partial_data.items():
        if isinstance(value, dict):
            text += "\n"
            text += f"class {soft_capitalize(key)}:\n"
            for attrib_name, attrib_value in value.items():
                if not isinstance(attrib_value, str):
                    text += f"    {attrib_name}: '{soft_capitalize(attrib_name)}'\n"
            text += _recursive_build_stub(value)
        else:
            text += f'    @staticmethod\n    def {key}() -> Literal["{value}"]: ...\n\n'
    return text


def _nested_dict_to_stub(nested_dict: Dict, root_class_name: str) -> str:
    stub_code = "from typing import Literal\n"
    stub_code += _recursive_build_stub({root_class_name: nested_dict})
    return stub_code
