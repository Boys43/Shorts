import asyncio, time, functools, weakref, random

class EventBus:
    def __init__(self): self._events = {}
    def on(self, evt, cb): self._events.setdefault(evt, []).append(cb)
    def emit(self, evt, *a, **kw):
        for cb in self._events.get(evt, []): cb(*a, **kw)

bus = EventBus()

class Cache:
    def __init__(self, ttl=3): self.ttl, self.data = ttl, {}
    def set(self, k, v): self.data[k] = (v, time.time() + self.ttl)
    def get(self, k):
        if k not in self.data: return None
        v, exp = self.data[k]
        if time.time() > exp: self.data.pop(k); return None
        return v

class Meta(type):
    def __call__(cls, *a, **kw):
        obj = super().__call__(*a, **kw)
        bus.emit("created", cls.__name__)
        return obj

class APIService(metaclass=Meta):
    def __init__(self, base, ttl=5):
        self.base, self.cache = base, Cache(ttl)

    async def fetch(self, endpoint):
        url = f"{self.base}{endpoint}"
        if cached := self.cache.get(url): return cached
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()
                self.cache.set(url, data)
                return data

class State:
    def __init__(self, **kw): self.__dict__["_data"] = kw
    def __getattr__(self, k): return self._data.get(k)
    def __setattr__(self, k, v):
        self._data[k] = v
        bus.emit("stateChange", k, v)

state = State(count=0, user=None)

def debounce(wait):
    def decorator(fn):
        last_call = {"handle": None}
        @functools.wraps(fn)
        async def wrapper(*a, **kw):
            if last_call["handle"]: last_call["handle"].cancel()
            loop = asyncio.get_event_loop()
            last_call["handle"] = loop.call_later(
                wait, lambda: asyncio.ensure_future(fn(*a, **kw))
            )
        return wrapper
    return decorator

def countdown(n):
    while n > 0:
        yield n
        n -= 1

# ---------- Context Manager ----------
class Timer:
    def __enter__(self): self.start = time.time(); return self
    def __exit__(self, *_): print("⏱ Elapsed:", round(time.time() - self.start, 3), "s")

# ---------- Example Usage ----------
@debounce(1)
async def search_user(name):
    res = await api.fetch(f"/users?username={name}")
    state.user = res[0] if res else None

async def main():
    bus.on("stateChange", lambda k, v: print(f"⚡ {k} → {v}"))
    bus.on("created", lambda n: print(f"🎉 Created {n}"))

    # Count with generator
    for x in countdown(3): print("⏳", x)

    # Async API
    with Timer():
        await search_user("Bret")
        await asyncio.sleep(2)
        await search_user("Antonette")  # only this runs (debounced)

# Run
api = APIService("https://jsonplaceholder.typicode.com")
asyncio.run(main())
