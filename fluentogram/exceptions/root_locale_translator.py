# coding=utf-8
"""Custom exception, raises when main, core translator does not exist"""


class NotImplementedRootLocaleTranslator(Exception):
    """
    This exception is raised when TranslatorHub has no translator for root locale and being impossible to work.
    """

    def __init__(self, root_locale) -> None:
        super().__init__(
            f"""\n
        You do not have a root locale translator.
        Root locale is "{root_locale}"
        Please, fix it!
        Just provide the data!
        """
        )
