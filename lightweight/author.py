from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Author:
    """An author. Mostly used by RSS/Atom."""
    name: Optional[str] = None
    email: Optional[str] = None
