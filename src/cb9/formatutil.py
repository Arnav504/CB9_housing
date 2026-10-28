"""Display helpers for generated markdown."""

from __future__ import annotations


def dollars(value: float, digits: int = 0) -> str:
    if digits == 0:
        return f"${value:,.0f}"
    return f"${value:,.{digits}f}"


def number(value: float, digits: int = 0) -> str:
    return f"{value:,.{digits}f}"


def percent(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}%"


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    def clean(cell: str) -> str:
        return str(cell).replace("|", "\\|").replace("\n", " ")

    head = "| " + " | ".join(clean(h) for h in headers) + " |"
    rule = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(clean(c) for c in row) + " |" for row in rows]
    return "\n".join([head, rule, *body]) + "\n"
