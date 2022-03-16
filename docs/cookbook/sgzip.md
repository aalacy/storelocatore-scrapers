# Dynamic Geospatial Search

#### Library version:

```
sgzip>=0.8.0
```

## Rationale (Why?)

- Many store locators use geographical location as input, and return a list of nearby stores.
- This input is often one of:
  - `zipcode` / `postal code`
  - `latitude & longitude`
- These inputs is what `sgzip` is intended to provide to crawl-writers.
- It also packs a lot of intelligence and optimization into the search, which will be covered in subsequent sections.

## When not to use sgzip

- When a single lat/long or zipcode query can return all locations in a country
  (e.g., by providing an enormous search radius or maximum number of search results, or else by omitting them - depends on the API.)
- Before using `sgzip`, play around with those limits, and see for yourself if you can fetch all results in one go.

## Note on Deduplication

- `sgzip` does not provide any guarantees about locations provided by store-locator APIs.
- Deduplication of locations must be performed on locations found using `sgzip`, as nearby points can overlap in the store-locator API.
- Use libraries such as `SgWriter`, `SimpleScraperPipeline` or `SgCrawler` to define unique identities (see cookbook.)

## Note on Persistence

- `sgzip` automatically uses the [Persistence / Pause-Resume](./pause_resume.md) functionality.
- Note that it will automatically write to, and pick up on any existing `state.json` file, and continue from there!

## Implementation (How?)

### SearchableCountries

- Import using:

```python
from sgzip.dynamic import SearchableCountries
```

- Contains all countries, for which we have maps.
- We have both zip/postal-code _and_ lat/long coverage for all countries in `SearchableCountries.WITH_ZIPCODE_AND_COORDS`.
- For most other countries, we have generated search coordinates, but don't have zip/postal-code data.
  - These you can find in `SearchableCountries.WITH_COORDS_ONLY`.
  - You can only use `DynamicGeoSearch` with these countries.
- For a full dataset of countries, use: `SearchableCountries.ALL`.

#### SovereigntyGroups

- We're living in a post-colonial world, where several of the world's powers still hold dominion over other semi-independent nations.
- For the cases where you need to fetch data from these territories, we have `SearchableCountries.SovereigntyGroups`
- It is simply a `dict` of a list of countries under a particular dominion, which is keyed on the ruling entity name.
- Here it is, as it stands now:
```python
SovereigntyGroups = {
    'UK': [BRITAIN, GUERNSEY, ISLE_OF_MAN, JERSEY, FALKLAND_ISLANDS_MALVINAS, GIBRALTAR],
    'DANISH': [DENMARK, FAROE_ISLANDS, GREENLAND],
    'FINISH': [FINLAND, ALAND_ISLANDS],
    'FRENCH': [FRANCE, FRENCH_GUIANA, GUADELOUPE, MARTINIQUE, MAYOTTE, NEW_CALEDONIA, REUNION,
               ST_PIERRE_AND_MICHELON, WALLIS_FUTUNA, FRENCH_POLYNESIA],
    'NORSE': [NORWAY, SVALBARD_JAN_MAYEN],
    'AMERICAN': [USA, AMERICAN_SAMOA, GUAM, N_MARIANA_ISL, PUERTO_RICO, VIRGIN_ISLANDS],
    'AUSTRALIAN': [AUSTRALIA, NORFOLK_ISLAND, CHRISTMAS_ISLAND]
}
```

### Dynamic Search

- Import using:

```python
# Keep the one you need:
from sgzip.dynamic import DynamicZipSearch, DynamicGeoSearch, DynamicZipAndGeoSearch
```

#### Three Types of Search

- `DynamicZipSearch`:
  - Will produce zip/postal-codes (`str`) when iterating:
    ```python
    search = DynamicZipSearch(...)
    for zipcode in search:
      ...
    ```
  - Only works with the countries, for which we have zip/postal-code coverage.
- `DynamicGeoSearch`:
  - Will produce a `latitude, longitude` tuple (`Tuple[float, float]`) when iterating:
    ```python
    search = DynamicGeoSearch(...)
    for lat, long in search:
      ...
    ```
  - Works with all countries.
- `DynamicZipAndGeoSearch`:
  - Will produce a tuple with both zip/postal-code, and the lat/long tuple when iterating:
    ```python
    search = DynamicZipAndGeoSearch(...)
    for zipcode, coord in search:
      lat, long = coord
      ...
    ```
  - Same capabilities and limitations as `DynamicZipSearch`

#### API

- The above three classes share the same API, including constructors (aside from the differences mentioned above.)
- Constructor API:

```python
def __init__(self,
             country_codes: List[str],
             max_search_distance_miles: float = 100,
             expected_search_radius_miles: Optional[float] = None,
             max_search_results: Optional[int] = None,
             granularity: ZipcodeGranularity = Grain_4(),
             debug_with_seed: Optional[Set[Tuple[float, float]]] = None):
    """
    :param country_codes: The search-space, as referenced in `SearchableCountries`.
    :param max_search_distance_miles: The outermost distance allowed for
    :param expected_search_radius_miles: [Optional; Optimization] The maximum radius we expect the search API to cover in a single query.
    :param max_search_results: [Optional; Optimization] The maximum number or results the search API will return in a single query.
    :param granularity: Choose between Grain_8(), Grain_4(), Grain_2(), Grain_1_KM() to control how many, and how close together
                        will the centroids be.
    :param debug_with_seed: [Only use when debugging a particular region] If present, filters out all other coordinates/zipcodes.
    """
```

- Public Methods:
  - ```python
    def found_location_at(self, latitude: Union[float, str], longitude: Union[float, str]):
        """
        Mark a location as found, iff it's no farther than `max_search_distance_miles`.
        Will throw a ValueError if latitude or longitude are invalid.
        """
    ```
  - ```python
    def items_remaining(self) -> int:
      """
      Returns the amount of zipcodes/coordinates remaining in the search-space.
      """
    ```
  - ```python
    def current_country(self) -> Optional[str]:
      """
      SgZip can run across several countries, but it does so sequentially.
      This method can help you get the country code for the country currently being traversed.
      You can then use `utils.country_names_by_code()` to find the human-readable country name for it.
      (should always exist if iterating using the `for X in DynamicXSearch` idiom).
      """
    ```
  - ```python
    def _current_coord(self) -> Optional[Tuple[float, float]]:
      """
      NOTE: Strongly consider using `DynamicZipAndGeoSearch` if you need this.
      Returns the coordinate in the current cursor, if exists
      (should always exist if iterating using the `for X in DynamicXSearch` idiom).
      """
    ```
  - ```python
    def _current_zip(self) -> Optional[str]:
      """
      NOTE: Strongly consider using `DynamicZipAndGeoSearch` if you need this.
      Returns the zipcode in the current cursor, if exists.
      (should always exist if iterating using the `for X in DynamicXSearch` idiom).
      """
      return self.__search.current_zip()
    ```

#### Example:

```python
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
search = DynamicGeoSearch(country_codes=[SearchableCountries.USA],
                          max_search_distance_miles = 100,
                          expected_search_radius_miles = 15,
                          max_search_results = None)
for lat, long in search:
    print (f'Coordinates remaining: {search.items_remaining()} For country: {search.current_country()}')
    coord_results = search_api(lat, long)
    # ... process/yield results here
    for lat, long in coord_results:
        search.found_location_at(lat, long)
```
