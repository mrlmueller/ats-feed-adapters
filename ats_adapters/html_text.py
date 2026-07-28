"""Minimaler HTML-zu-Text-Helfer für Feed-Beschreibungen."""
from __future__ import annotations

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    return html.unescape(_TAG_RE.sub(" ", text)).strip()
