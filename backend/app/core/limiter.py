"""
Shared slowapi Limiter instance.

Lives in its own module (not main.py) so router modules can import it directly
for @limiter.limit(...) decorators without creating an import cycle with main.py.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
