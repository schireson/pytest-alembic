"""The failure type the built-in tests raise, and how its context is rendered."""

import textwrap


class AlembicTestFailure(AssertionError):  # noqa: N818
    """A built-in test failure, carrying labelled context to print beneath the message.

    Subclasses :class:`AssertionError` so a migration problem reports as an ordinary
    test failure rather than an error — the distinction pytest draws between "the code
    under test is wrong" and "the test itself broke".

    The context exists because the useful part of a migration failure is usually a diff
    or a revision listing, which is unreadable squeezed onto the assertion line.
    """

    def __init__(self, message, context=None):
        """Build the failure.

        Args:
            message: The one-line failure message.
            context: Optional ``(title, body)`` pairs rendered as indented blocks.
        """
        super().__init__(message)
        self.context = context
        self.exce = self
        self.item = None

    def format_context(self) -> list[str]:
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
