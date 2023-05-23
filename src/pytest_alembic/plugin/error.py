import textwrap
from typing import List


class AlembicTestFailure(AssertionError):  # noqa: N818
    def __init__(self, message, context=None):
        super().__init__(message)
        self.context = context
        self.exce = self
        self.item = None

    def format_context(self) -> List[str]:
        """Print out a custom error message to the terminal."""
        result = []
        if not self.context:
            return []

        for title, item in self.context:
            result.extend(["", f"{title}:", textwrap.indent(item, "    ")])
        return result

    def __str__(self):
        content = self.format_context()
        segments = [super().__str__(), *content]
        return "\n".join(segments)
