# Pausing and Resuming Long-Running Crawls

### Library version:

```
sgscrape>=0.1.7
```

## Rationale (Why?)

- We're currently using Apify to execute our crawlers.
- Apify does not promise to run a crawler start-to-finish in one go.
- Instead, they might stop the instance running crawler, and resume execution on a different machine.
- They provide some persistent cloud storage to save the crawl state, which we'll utilize behind the scenes.

## Implementation (How?)

### Best Practices & Dos And Don'ts:

- Always use either an `SgWriter`, `SimpleScraperPipeline` or else an `SgCrawler` to deduplicate & persist records.
- Never create a list of results that you return.
- Instead, always `yield` each result as it arrives.
- When using `sgzip`, never create multiple `DynamicXSearch` instances (e.g. per-country.)
- Instead, always pass all countries to `sgzip`, via `SearchableCountries.ALL`
- If you're initializing a persistent value, use the `default_factory` parameter of `state.get_misc_value`.

### Bare-bones, just requests:

- This is a bare-bones example for how to implement a scraper/crawler which pause/resumes, with an initial phase that
  uses a site-map.
- Take special note how `record_initial_requests` is being called only once via `state.get_misc_value` with the `default_factory` method.

```python
from typing import Iterable

from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sgscrape.sgrecord_id import SgRecordID, RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests

def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    # use the http session (or sgselenium) to fetch, and then register all (or most) requests
    # in the CrawlState, so that it persists them if/when the crawler is restarted on another machine.

    sitemap = http.get('http://example.com/sitemap').json()
    for page in sitemap['locations']:
        # note the context dict - it's used to encode the meaning/context of each request,
        # so that you can understand what each request signifies later.
        if page['type'] == 'branch':
            state.push_request(
                SerializableRequest(url=page['url'], context={'type': 1})
            )
        elif page['type'] == 'office':
            state.push_request(
                SerializableRequest(url=page['url'], context={'type': 2})
            )

    return True  # signal that we've initialized the request queue.

def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    # note - you can still use `state.push_request(...)` while using this iterator!
    for next_r in state.request_stack_iter():
        if next_r.context.get('type') == 1:
            location = http.get(next_r.url).json()
            yield SgRecord(raw_address=location)
        elif next_r.context.get('type') == 2:
            location = http.get(next_r.url).request.body
            yield SgRecord(raw_address=location)
        else:
            raise ValueError(f'Cannot decode context: {next_r.context}')

if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        with SgRequests() as http:
            state.get_misc_value('init', default_factory=lambda: record_initial_requests(http, state))
            for rec in fetch_records(http, state):
                writer.write_row(rec)
```

### Bare-bones, with sgzip:

- There is _nothing_ special that you need to do here, aside from following the best practices at the start of the page.
- This example will be a bit more elaborate, to showcase the capabilities of the libraries.
- In the end, it will tell us how many locations were found in each country.

```python
from typing import Iterable

from sgscrape.sgrecord_id import SgRecordID, RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
  state = CrawlStateSingleton.get_instance()
  for lat, lng in search:
      rec_count = state.get_misc_value(search.current_country(), default_factory=lambda: 0)
      state.set_misc_value(search.current_country(), rec_count + 1)
      location = http.get(f'http://example.com/coord/{lat}/{lng}').json()
      yield SgRecord(raw_address=location)

if __name__ == "__main__":
    search = DynamicGeoSearch(country_codes=SearchableCountries.ALL)
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
    print("Printing number of records by country-code:")
    for country_code in SearchableCountries.ALL:
        print(country_code, ": ", state.get_misc_value(country_code, default_factory=lambda: 0))
```
