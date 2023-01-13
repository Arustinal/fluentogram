from fluentogram import AttribTracer


class StubsTranslatorRunner(AttribTracer):
    def __init__(self):
        super().__init__()
        self.kwargs = {}

    def __call__(self, **kwargs):
        out = self._get_request_line()[:-1], kwargs
        self.request_line = ""
        return out
