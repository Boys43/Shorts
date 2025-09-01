<?php
declare(strict_types=1);

#[Attribute(Attribute::TARGET_FUNCTION | Attribute::TARGET_METHOD)]
class Memoize {
    public function __construct(public int $ttlSeconds = 5) {}
}

final class TTLCache {
    private array $store = []; // key => [expires, value]
    public function set(string $key, mixed $value, int $ttl): void {
        $this->store[$key] = [time() + $ttl, $value];
    }
    public function get(string $key): mixed {
        if (!isset($this->store[$key])) return null;
        [$exp, $val] = $this->store[$key];
        if ($exp < time()) { unset($this->store[$key]); return null; }
        return $val;
    }
}

final class EventBus {
    /** @var array<string, list<callable>> */
    private array $listeners = [];
    public function on(string $event, callable $cb): void {
        $this->listeners[$event][] = $cb;
    }
    public function emit(string $event, mixed ...$payload): void {
        foreach ($this->listeners[$event] ?? [] as $cb) {
            $cb(...$payload);
        }
    }
}

final class ReactiveState implements ArrayAccess, IteratorAggregate, Countable {
    private array $data;
    public function __construct(private EventBus $bus, array $initial = []) {
        $this->data = $initial;
    }
    public function __get(string $k): mixed { return $this->data[$k] ?? null; }
    public function __set(string $k, mixed $v): void { $this->data[$k] = $v; $this->bus->emit('state:change', $k, $v); }
    public function offsetExists(mixed $o): bool { return array_key_exists($o, $this->data); }
    public function offsetGet(mixed $o): mixed { return $this->data[$o] ?? null; }
    public function offsetSet(mixed $o, mixed $v): void { $this->__set((string)$o, $v); }
    public function offsetUnset(mixed $o): void { unset($this->data[$o]); $this->bus->emit('state:change', (string)$o, null); }
    public function getIterator(): Traversable { yield from $this->data; }
    public function count(): int { return count($this->data); }
}

/** Simple middleware pipeline (request -> ... -> response) */
final class Pipeline {
    /** @var list<callable> */
    private array $layers = [];
    public function through(callable ...$layers): self { $this->layers = $layers; return $this; }
    public function process(mixed $request): mixed {
        $carry = fn($req, $i) => $i < count($this->layers)
            ? ($this->layers[$i])($req, fn($r) => $carry($r, $i+1))
            : $req;
        return $carry($request, 0);
    }
}

/** Concurrent HTTP client using curl_multi */
final class Http {
    public function __construct(private ?TTLCache $cache = null) {}
    public function get(string $url, ?int $ttl = n
