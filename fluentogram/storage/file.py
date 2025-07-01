from __future__ import annotations

from pathlib import Path

from fluent_compiler.bundle import FluentBundle

from fluentogram.exceptions import LocalesNotFoundError
from fluentogram.storage.base import BaseStorage
from fluentogram.translator import FluentTranslator


class FileStorage(BaseStorage):
    def __init__(self, path: str | Path, use_isolating: bool = False) -> None:  # noqa: FBT002
        super().__init__()
        self.path = Path(path)
        self.use_isolating = use_isolating
        self._load_translations()

    def _extract_locales(self, path: Path) -> list[str]:
        if "{locale}" in path.parts:
            path = Path(*path.parts[: path.parts.index("{locale}")])

        locales: list[str] = [file_path.name for file_path in path.iterdir() if file_path.is_dir()]

        if not locales:
            raise LocalesNotFoundError(locales=[], path=path.as_posix())

        return locales

    @staticmethod
    def _find_locales(
        path: Path,
        locales: list[str],
    ) -> dict[str, list[Path]]:
        paths: dict[str, list[Path]] = {}

        if "{locale}" not in path.as_posix():
            path = path.joinpath("{locale}")

        for locale in locales:
            locale_path = Path(path.as_posix().format(locale=locale))
            recursive_paths = locale_path.rglob("*.ftl")  # Will recursively search for files
            paths.setdefault(locale, []).extend(recursive_paths)

            if not paths[locale]:
                raise LocalesNotFoundError(locales=locales, path=locale_path.as_posix())

        return paths

    def _load_translations(self) -> None:
        locales = self._extract_locales(self.path)
        for locale, paths in self._find_locales(self.path, locales).items():
            texts = [path.read_text(encoding="utf8") for path in paths]

            self.add_translator(
                FluentTranslator(
                    locale=locale,
                    translator=FluentBundle.from_string(
                        text="\n".join(texts),
                        locale=locale,
                        use_isolating=self.use_isolating,
                    ),
                ),
            )

    async def close(self) -> None:
        pass
