# Records And Identity

#### Library version:

```
sgscrape>=0.1.8
```

## The idea of a Location record

- Normally, we write each record we find using the store-locator to the data-file.
- See this document section for the [data requirements](https://docs.google.com/document/d/1LZEzE2lmhOAtAb8jgnVUjKyTzxblEBTvO-XaF6C5k6g/edit#heading=h.ycquafkz8bzd) of each record.
- We encapsulate this concept using an `SgRecord`
- **Do not use raw lists to represent records!** (This is bad: `[id, MISSING, url, ...]`)

### SgRecord

- Import statement:

```python
from sgscrape.sgrecord import SgRecord
```

- An empty field is represented by `SgRecord.MISSING`.
  - Please, use that instead of hardcoding `"<MISSING>"` since:
    - You can make a small typo.
    - We can change it down the line, and by referencing a library constant, you will not need to change your scripts.
- The best way to instantiate a record, is by using the fields in the constructor:

```
SgRecord(
 page_url: str = SgRecord.MISSING,
 location_name: str = SgRecord.MISSING,
 street_address: str = SgRecord.MISSING,
 city: str = SgRecord.MISSING,
 state: str = SgRecord.MISSING,
 zip_postal: str = SgRecord.MISSING,
 country_code: str = SgRecord.MISSING,
 store_number: str = SgRecord.MISSING,
 phone: str = SgRecord.MISSING,
 location_type: str = SgRecord.MISSING,
 latitude: str = SgRecord.MISSING,
 longitude: str = SgRecord.MISSING,
 locator_domain: str = SgRecord.MISSING,
 hours_of_operation: str = SgRecord.MISSING,
 raw_address: str = SgRecord.MISSING
)
```

- You can access all the fields using accessor methods with the same name.

  - e.g. `record.locator_domain()`

- Methods you normally DO NOT need:
  - You can also see the record as a list `record.as_row()`
  - Or as a dict: `record.as_dict()`

## Record Identity

- We need to ensure that each record that is written to the file is unique.
- For that, we need to define a _record identity_ that is unique per record.
- A record identity will consist of one or more of the record's fields.

### Two Methods

- As a crawl-writer, you have two ways to define the record's identity:
  - Using the [SimpleScraperPipeline](./declarative_pipeline.md) (will also simplify writing to file, transforming, filtering etc.)
  - Passing an `SgRecordDeduper` that uses a `SgRecordID`, to the `SgWriter` (more on that in a second, but first...)
- What NOT to do:

```python
ids = []  # or even a set()
```

### `SgRecordID`, `SgRecordDeduper`

- When instantiating an `SgWriter`, it will as you to provide an `SgRecordDeduper`. That is done so the writer will not produce
  duplicates to the `data.csv` file - either from new or existing sources (that is, if the crawl is resumed after a pause.)
- An `SgRecordDeduper` requires an `SgRecordId`.
- An `SgRecordID` has three constructor fields:
  - `id_fields: Set[SgRecord.Headers.HeaderUnion]`: A set of the field names, as defined in `SgRecord.Headers`
  - `fail_on_empty_field: bool = False`: Should we raise a `ValueError` if a single identity-field is empty for a given record?
  - `fail_on_empty_id: bool = True`: Should we raise a `ValueError` if the entire identity is empty for a given record?
  - `transformations: Dict[SgRecord.Headers.HeaderUnion, Tuple[str, Callable[[Any], str]]] = {}`: Should some identity fields be massaged before they're used to compute the identity?
- This is a handful, so let's look at some already-available record IDs you can use off-the-shelf. This is in `sgscrape.sgrecord_id`:

```python
class RecommendedRecordIds:
    PhoneNumberId = SgRecordID({SgRecord.Headers.PHONE}, fail_on_empty_id=True)
    GeoSpatialId = SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE}, fail_on_empty_id=True)\
                     .with_truncate(SgRecord.Headers.LATITUDE, 3)\
                     .with_truncate(SgRecord.Headers.LONGITUDE, 3)
    StoreNumberId = SgRecordID({SgRecord.Headers.STORE_NUMBER}, fail_on_empty_id=True)
    PageUrlId = SgRecordID({SgRecord.Headers.PAGE_URL}, fail_on_empty_id=True)
    StoreNumAndPageUrlId = SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.PAGE_URL}, fail_on_empty_id=True)
```

- And now we can instantiate the `SgRecordDeduper`:

```python
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

# This will deduplicate records based on their store_number.
deduper = SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
```
