# Shared rate limiter (slowapi). Keyed by client IP.
# Routers import `limiter` to decorate expensive endpoints; main.py registers
# the limiter on the app and the 429 handler.
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
