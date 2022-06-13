# Parallel Dynamic Geospatial Search

#### Library version:

```
sgzip>=0.11.0
```

### Required reading: [Dynamic Geospatial Search (Link)](./sgzip.md)

## Rationale (Why?)

- Traversing multi-national APIs using dynamic geo search sequentially is very slow, due to the sheer amount of centroids.
- It can get so slow, that it takes several days to complete one crawl.
- The parallel search was created to address those issues.
- Parallel dynamic geospatial search allows you to use asynchronous API calls (anything that uses HTTP, for example) to
  traverse each country in a separate thread.
- This lends itself to significant speed gains.

## Implementation (How?)

- You will be using three classes from a single module:
  - `from sgzip.parallel import DynamicSearchMaker, SearchIteration, ParallelDynamicSearch`
  - `DynamicSearchMaker`:
    - It is a factory class that allows you to define a `Dynamic*Search` without specifying the country codes.
    - In addition to having all the familiar constructor params, it asks for a `search_type`:
      - One of: `'DynamicZipSearch', 'DynamicGeoSearch', 'DynamicZipAndGeoSearch'`
  - `SearchIteration`:
    - You need to inherit from this class, and override the `do` method.
    - In the `do` method, you will use the info given to you at each search iteration,
      to `yield` the records.
    - See example below for enhanced clarity.
  - `ParallelDynamicSearch`:
    - This is the engine that brings the abovementioned classes together.
    - Here, you inject instances of the previous classes, specify the `country_codes`.
    - See example below for enhanced clarity.
    - When injecting the `search_iteration` argument, you can **either** provide an instance, or a function that returns the instance.
      - If you provided a function, an instance will be created _per country_.
      - This is a good way to inject an HTTP client, since sgzip will work sequentially within a country in any case.
      - You can see the function injected in the example below.

```python
from typing import Iterable, T_co, Tuple, Callable
from sgscrape.sgrecord_id import SgRecordID, RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration


class ExampleSearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """
    def __init__(self):
        self.__http = SgRequests()  # Leaks resources, but it's ok.
        self.__state = CrawlStateSingleton.get_instance()

    def do(self,
           coord: Tuple[float, float],
           zipcode: str,
           current_country: str,
           items_remaining: int,
           found_location_at: Callable[[float, float], None]) -> Iterable[SgRecord]:
        """
        This method gets called on each iteration of the search.
        It provides you with all the data you could get from the search instance, as well as
        a method to register found locations.

        :param coord: The current coordinate (lat, long)
        :param zipcode: The current zipcode (In DynamicGeoSearch instances, please ignore!)
        :param current_country: The current country (don't assume continuity between calls - it's meant to be parallelized)
        :param items_remaining: Items remaining in the search - per country, if `ParallelDynamicSearch` is used.
        :param found_location_at: The equivalent of `search.found_location_at(lat, long)`
        """

        # here you'd use self.__http, and call `found_location_at(lat, long)` for all records you find.
        http.get('http://example.com')

        # just some clever accounting of locations/country:
        rec_count = self.__state.get_misc_value(current_country, default_factory=lambda: 0)
        self.__state.set_misc_value(current_country, rec_count + 1)

        yield SgRecord(zip_postal=zipcode,
                       latitude=coord[0],
                       longitude=coord[1],
                       country_code=current_country)


if __name__ == "__main__":
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(search_type='DynamicGeoSearch', granularity=Grain_8())

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        par_search = ParallelDynamicSearch(search_maker=search_maker,
                                           search_iteration=lambda: ExampleSearchIteration(),
                                           country_codes=SearchableCountries.ALL)

        for rec in par_search.run():
            writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
    print("Printing number of records by country-code:")
    for country_code in SearchableCountries.ALL:
        print(country_code, ": ", state.get_misc_value(country_code, default_factory=lambda: 0))

```
