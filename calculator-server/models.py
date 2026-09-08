import re
from datetime import datetime

from pydantic import BaseModel


class Expression(BaseModel):
    """Request body for POST /calculate."""

    expr: str

    @staticmethod
    def expand_percent(expr: str) -> str:
        """Handle A op B% and standalone N% patterns."""
        _percent_pair = re.compile(
            r"""(?P<a>\d+(?:\.\d+)?)\s*(?P<op>[+\-*/])\s*(?P<b>\d+(?:\.\d+)?)%""",
            re.VERBOSE,
        )
        _number_percent = re.compile(r"(?P<n>\d+(?:\.\d+)?)%")

        s = expr
        while True:
            # Replace A op B%
            m = _percent_pair.search(s)
            if not m:
                break
            a, op, b = m.group("a", "op", "b")
            if op in "+-":
                repl = f"{a} {op} (({b}/100)*{a})"
            elif op == "*":
                repl = f"{a} * ({b}/100)"
            else:
                repl = f"{a} / ({b}/100)"
            s = s[: m.start()] + repl + s[m.end() :]

        # Replace B%
        s = _number_percent.sub(lambda m: f"({m.group('n')}/100)", s)
        return s


class CalculatorLog(BaseModel):
    """One entry of the calculation history."""

    timestamp: datetime | None = None
    expr: str
    result: float