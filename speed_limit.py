# speed_limit.py
# Bandwidth throttling per config using a debt-based token bucket.
# FIX (v2.0): the previous bucket dead-locked when a single chunk was larger
# than the bucket capacity (e.g. 256KB reads with a sub-2Mbit/s limit). The new
# implementation lets the token balance go negative and simply waits for the
# debt to be repaid, so it can never stall regardless of chunk size.
import asyncio
import time

from state import LINKS

_buckets: dict = {}

MIN_RATE = 1024          # 1 KB/s floor to avoid divide-by-zero / absurd rates
MIN_BURST = 64 * 1024    # minimum burst capacity


class _Bucket:
    __slots__ = ("rate", "capacity", "tokens", "last")

    def __init__(self, rate_bytes_per_sec: float):
        self.rate = max(rate_bytes_per_sec, MIN_RATE)
        self.capacity = max(self.rate, MIN_BURST)
        self.tokens = self.capacity
        self.last = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last
        if elapsed > 0:
            self.last = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

    async def consume(self, n: int):
        # Debt-based: subtract immediately, then wait until the balance recovers.
        # This is correct for any n, including n much larger than capacity.
        self._refill()
        self.tokens -= n
        while self.tokens < 0:
            wait = min(-self.tokens / self.rate, 0.5)
            await asyncio.sleep(max(wait, 0.001))
            self._refill()


def _get_bucket(uuid: str, rate: int) -> _Bucket:
    b = _buckets.get(uuid)
    if b is None or b.rate != max(rate, MIN_RATE):
        b = _Bucket(rate)
        _buckets[uuid] = b
    return b


async def throttle(uuid: str, nbytes: int):
    if nbytes <= 0:
        return
    link = LINKS.get(uuid)
    rate = int((link or {}).get("speed_limit_bytes", 0) or 0)
    if rate <= 0:
        return
    bucket = _get_bucket(uuid, rate)
    await bucket.consume(nbytes)


def reset_bucket(uuid: str):
    _buckets.pop(uuid, None)
