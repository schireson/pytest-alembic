import textwrap

from _pytest._code.code import FormattedExcinfo


class AlembicTestFailure(AssertionError):
    def __init__(self, message, context=None):
        super().__init__(message)
        self.context = context


class AlembicReprError:
    def __init__(self, exce, item):
        self.exce = exce
        self.item = item

    def toterminal(self, tw):
        """Print out a custom error message to the terminal."""
        exc = self.exce.value
        context = exc.context

        if context:
            for title, item in context:
                tw.line(title + ":", white=True, bold=True)
                tw.line(textwrap.indent(item, "    "), red=True)
                tw.line("")

        e = FormattedExcinfo()
        lines = e.get_exconly(self.exce)

        tw.line("Errors:", white=True, bold=True)
        for line in lines:
            tw.line(line, red=True, bold=True)
