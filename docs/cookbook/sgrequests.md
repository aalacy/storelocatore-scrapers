# Using SgRequests

#### Library version:

```
sgrequests>=0.2.0
```

## Features

- Uses the excellent [httpx](https://www.python-httpx.org/) library.
- Fully [http2-compatible](https://en.wikipedia.org/wiki/HTTP/2).
- When a proxy is configured, rotates proxy addresses in case of errors.
- Configurable timeout and retry policies.
- Convenient API for dealing with errors.
- Dual API for both synchronous and async operations, using the full capabilities of nonblocking [asyncio](https://docs.python.org/3.8/library/asyncio.html).

## Useful Constants and helper classes:

```python
from typing import Optional
from dataclasses import dataclass
from httpx import Timeout, Request, Response

class SgRequestsAsync:
  DEFAULT_RETRIES = 3
  DEFAULT_TIMEOUT = Timeout(timeout=61, connect=61)
  DEFAULT_PROXY_URL = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"
  DEFAULT_DONT_RETRY_STATUS_CODES = frozenset(range(400, 600))  # set([400, 401, ..., 599])

@dataclass(frozen=True)
class SgRequestError(Exception):
    """
    Communicates all errors, alongside with the context in which the error was made.
    """
    request: Optional[Request] = None
    response: Optional[Response] = None
    status_code: Optional[int] = response.status_code if response else None
    message: Optional[str] = None
    base_exception: Optional[Exception] = None
```

## `SgRequests` constructor with docs:

- `SgRequests` is meant to be self-explanatory, and fully-configurable via the constructor.
- Proxy configuration is done via environment vars, injected by the runtime (or set during a test):
  - `PROXY_PASSWORD`
  - `PROXY_URL`

```python
class SgRequests(SgRequestsAsync):
  def __init__(self,
               proxy_country: Optional[str] = None,
               dont_retry_status_codes: Set[int] = SgRequestsAsync.DEFAULT_DONT_RETRY_STATUS_CODES,
               dont_retry_status_codes_exceptions: Set[int] = frozenset(),
               timeout_config: Timeout = SgRequestsAsync.DEFAULT_TIMEOUT,
               retries_with_fresh_proxy_ip: int = 4):
      """
      Synchronous SgRequests, backed by httpx, with proxy rotation and lots of customization.
      :param proxy_country: [None] Optionally, override the default proxy 2-letter country code
                            (`us` at the time of writing).
      :param dont_retry_status_codes: [SgRequestsAsync.DEFAULT_DONT_RETRY_STATUS_CODES] Skip retries for these status codes.
      :param dont_retry_status_codes_exceptions: Exceptions to `dont_retry_status_codes`. Defaults to an empty set.
      :param timeout_config: [SgRequests.DEFAULT_TIMEOUT] HTTP timeout configuration. See `httpx`'s Timeout object.
      :param retries_with_fresh_proxy_ip: [4] How many times to rotate proxy IPs on errors,
                                              for each request errors before giving up?
      """
```

### Basic `SgRequests` in Action:

```python
import httpx
from sgrequests import SgRequests, SgRequestError

with SgRequests() as http:
    response = http.get(url='http://example.com')
    assert(isinstance(response, httpx.Response))
    assert(200 == response.status_code)

    # Error:
    err = http.put(url='http://example.com', data={})
    assert(isinstance(err, SgRequestError))
    assert(504 == err.status_code)

    # Alternatively, using try-catch control-flow:
    try:
        response = SgRequests.raise_on_err(http.put(url='http://example.com', data={}))
        assert(isinstance(response, httpx.Response))
        assert(200 == response.status_code)
    except SgRequestError as e:
        print(e.status_code)

```

### `SgRequests` instance methods:

- The idea is for the instance to be fully configurable through the constructor.
  - however sometimes you need extra control during execution.

```python
with SgRequests() as http:
    http.clear_cookies()  # For when you need to reset the state
    http.set_proxy_url(proxy_url)  # You shouldn't need to use that, but it changes the proxy url, and refreshes the session.
```

## Asynchronous `SgRequestsAsync` API

- Uses [asyncio](https://docs.python.org/3.8/library/asyncio.html) non-blocking calls.
- More efficient resource usage than threading.
- Identical constructor API to [SgRequests](#sgrequests-constructor-with-docs) (see above.)
- **Important Caveat**: `SgRequestsAsync` should never be instantiated outside of a `with` block!

### Basic `SgRequestsAsync` in Action:

```python
from typing import AsyncGenerator
from dataclasses import dataclass
from httpx import Response
import asyncio
from sgrequests import SgRequestsAsync

@dataclass
class State:
    good_counter = 0
    bad_counter = 0

async def producer():
    async with SgRequestsAsync() as http:
        yield await http.get('http://example.com/')
        yield await http.get('http://example.com/BOOM_EXPLOSION')  # 404 Error!
        yield await http.get('http://example.com/')

async def consumer(resp_generator: AsyncGenerator, state: State):
    async for response in resp_generator:
        if isinstance(response, Response):
            state.good_counter += 1
            assert(200 == response.status_code)
        else:
            state.bad_counter += 1
            assert(404 == response.status_code)

state = State()

asyncio.get_event_loop().run_until_complete(consumer(producer(), state))

assert(2 == state.good_counter)
assert(1 == state.bad_counter)
```
