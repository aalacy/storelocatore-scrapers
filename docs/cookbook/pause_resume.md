from typing import Iterablefrom typing import List# Pausing and Resuming Long-Running Crawls

## Rationale (Why?)

- We're currently using Apify to execute our crawlers.
- Apify does not promise to run a crawler start-to-finish in one go.
- Instead, they might stop the instance running crawler, and resume execution on a different machine.
- They provide some persistent cloud storage to save the crawl state, which we'll utilize behind the scenes.

## Implementation (How?)

### Bare-bones, just requests:

- This is a bare-bones example for how to implement a scraper/crawler which pause/resumes:

```python
from typing import Iterable

form sgscrape.pause_resume import SerializableRequest, CrawlState
from sgscrape.sgrecord_id import SgRecordID, RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests

def record_initial_requests(http: SgRequests, state: CrawlState):
    # use the http session (or sgselenium!) to fetch, and then register all (or most) requests
    # in the CrawlState, so that it persists them if/when the crawler is restarted on another machine.

    sitemap = http.get('http://example.com/sitemap').json()
    branches = state.get_misc_value('branches') or 0
    offices = state.get_misc_value('offices') or 0

    for page in sitemap['locations']:
        # note the context dict - it's used to encode the meaning/context of each request,
        # so that you can understand what each request signifies later.
        if page['type'] == 'branch':
            state.push_request(
                SerializableRequest(url=page['url'], context={'type': 1})
            )
            branches +=1
            state.set_misc_value('branches', branches)
        elif page['type'] == 'office':
            state.push_request(
                SerializableRequest(url=page['url'], context={'type': 2})
            )
            offices += 1
            state.set_misc_value('offices', offices)


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    next_r = state.pop_request()
    while next_r:
        # here you use the requests session to fetch the location from the requests
        if next_r.context.get('type') == 1:
            location = http.get(next_r.url).json()
            yield SgRecord(raw_address=location)
        elif next_r.context.get('type') == 2:
            location = http.get(next_r.url).request.body
            yield SgRecord(raw_address=location)
        else:
            raise ValueError(f'Cannot decode context: {next_r.context}')


if __name__ == "__main__":
    state = CrawlState()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        with SgRequests() as http:
            record_initial_requests(http, state)
            for rec in fetch_records(http, state):
                writer.write_row(rec)
                state.save_state()

    print(f'Branches: {state.get_misc_value("branches")}')
    print(f'Offices: {state.get_misc_value("offices")}')
```

### Bare-bones, with sgzip:

- This is a bare-bones example for how to implement a scraper/crawler which pause/resumes, that includes sgzip:

```python
from typing import Iterable

form sgscrape.pause_resume import SerializableRequest, CrawlState
from sgscrape.sgrecord_id import SgRecordID, RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

def record_initial_requests(http: SgRequests, search: DynamicGeoSearch, state: CrawlState):
    # use the http session (or sgselenium), and dynamic search to register all (or most) requests in the CrawlState,
    # so that it persists them if/when the crawler is restarted on another machine.

    for lat, lng in search:
        state.push_request(
            SerializableRequest(url=f'http://example.com/coord/{lat}/{lng}')
        )

def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    next_r = state.pop_request()
    while next_r:
        # here you use the requests session to fetch the location from the requests
        location = http.get(next_r.url).json()
        yield SgRecord(raw_address=location)


if __name__ == "__main__":
    state = CrawlState()
    # we inject the state into DynamicGeoSearch, which will automatically prune all previously-searched points,
    # and register new ones.
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA], state=state)
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        with SgRequests() as http:
            record_initial_requests(http, search, state)
            for rec in fetch_records(http, state):
                writer.write_row(rec)
                state.save_state()
```
