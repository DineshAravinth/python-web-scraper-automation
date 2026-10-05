from itertools import cycle


class ProxyManager:
    """Manages and rotates through a list of authorized proxies."""

    def __init__(self, proxies=None):
        self.proxies = proxies or []
        self._proxy_cycle = cycle(self.proxies) if self.proxies else None

    def get_next_proxy(self):
        """Return the next proxy in the rotation."""
        if not self._proxy_cycle:
            return None

        return next(self._proxy_cycle)

    def has_proxies(self):
        """Return True if proxies are configured."""
        return bool(self.proxies)

    def get_proxy_count(self):
        """Return the number of configured proxies."""
        return len(self.proxies)