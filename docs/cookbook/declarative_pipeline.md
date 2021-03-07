# Cookbook - Declarative Field Mapping

## Purpose
1. To increase clarity of intent when writing crawlers.
1. To decrease the amount of code written.
1. To reduce code variability.

## Benefits vs. Drawbacks / A Message of Caution and Hope:
This approach will feel foreign to many at first, however it has been shown to increase productivity in the short-medium
term, with less bugs, and make the process more enjoyable. All in all, the crawlers this approach produces versus the 
fully-manual, imperative approach are shorter, with much less code branches. That said, there are certain areas, where
experience will dictate better results, faster. That is to say, **if you get stuck, ask for help.**

## TL;DR
Skip to the [example at the bottom of the page](#example) to see it in action.

## Method
Building on `sgscrape.simple_scraper_pipeline.*`, we incorporate the field and pipeline definitions into the `sgcrawler`
framework.

## Basic Anatomy
You will need to supply an `sgscrape.simple_scraper_pipeline.SSPFieldDefinitions` to your Transformer/Filter, like so:
```python
DeclarativeTransformerAndFilter(
    pipeline=DeclarativePipeline(
        crawler_domain=crawler_domain,
        field_definitions=SSPFieldDefinitions( ... ),
        fail_on_outlier=False)  # Do we fail with an Exception on violating field definition constraint?
)
```
Which can be then plugged into any `SgCrawler` constructor.

### SSPFieldDefinitions
* These definitions tell us how to map between the a __raw__ data row (must be in the form of a `dict`) and all the 
  fields present in the final record.
* There are several ways to map data, which are all subclasses of `_FieldDefBase`:

#### MissingField
* Constructor: 
```python
MissingField()
```
* Always outputs `'<MISSING>'`.

#### ConstantField
* Constructor:
```python
ConstantField("constant value")
```
* Always outputs the same constant value.

#### MappingField
* Constructor and documentation:
```python
MappingField(
    mapping: List[str],
    value_transform: Optional[Callable[[str], str]] = None,
    raw_value_transform: Optional[Callable[[Any], str]] = None,
    part_of_record_identity: bool = False,
    is_required: bool = True
)

"""
Represents a field definition with a single field mapping.

:param mapping: Given a raw record in `dict` form, a mapping is the path to the field's value.
                For example, in { address: { street1: "..." } } the path of `street_address`
                would be `['address', 'street1']`.
:param value_transform: If the field's final value needs to be transformed, supply a lambda: str->str
:param raw_value_transform: Optionally, transforms a list of raw values (dense array with None fillers) into a str.
:param part_of_record_identity: Is this field part of the record's identity?
:param is_required: Is this field required to be present in a record, or can it be <MISSING>?
"""
```

#### MultiMappingField
* Constructor and documentation:
```python
MultiMappingField(
    mapping: List[List[str]],
    part_of_record_identity: bool = False,
    value_transform: Optional[Callable[[str], str]] = None,
    raw_value_transform: Optional[Callable[[list], str]] = None,
    is_required: bool = True,
    multi_mapping_concat_with: str = ' '
)

"""
Represents a field definition with a multiple field mappings.

:param mapping: In cases where multiple raw fields need to be concatenated to form a single logical field,
                a list of lists should be provided, such as in: { address: { street1: "...", street2: "..." } }
                and the `street_address` could be `[['address', 'street1'], ['address', 'street2']]`.
                In this case, the fields will be joined with the value of the `multi_mapping_concat_with` param.
:param value_transform: If the field's final value needs to be transformed, supply a lambda: str->str
:param raw_value_transform: Optionally, transforms a list of raw values (dense array with None fillers) into a str.
:param part_of_record_identity: Is this field part of the record's identity?
:param is_required: Is this field required to be present in a record, or can it be <MISSING>?
:param multi_mapping_concat_with: If we're dealing with multi-concat field mapping, this is the delimiter between
                                          the raw concatenated fields.
"""

```

## Implementation Details
The idea is to supply a `RecordTransformerAndFilter` to an implementation of `SgCrawler`, which exposes a declarative API.
This is achieved via the `DeclarativeTransformerAndFilter`, which accepts a `DeclarativePipeline` - a subclass of the 
`sgscrape.simple_scraper_pipeline.SimpleScraperPipeline` that hides certain features, and disables its ability to run. 
In turn, it accepts `sgscrape.simple_scraper_pipeline.SSPFieldDefinitions`, which are the hardcoded mappings between 
`SgRecord` fields, and how they are to be interpreted.

## Example
This is a full, working example of a crawler using this toolset.
```python
from sgcrawler.sgcrawler_fun import SgCrawlerUsingHttpFun
from sgcrawler.helper_definitions import DeclarativeTransformerAndFilter, DeclarativePipeline
from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import SSPFieldDefinitions, ConstantField, MappingField, MultiMappingField, MissingField
from sgscrape.simple_utils import ms_since_epoch
from sgscrape.sgwriter import SgWriter

def fetch_data(_, http: SgRequests):
    # Must yield raw dicts
    
    res = http.request(url="https://svc.moxiworks.com/service/v1/profile/offices/search",
                       data={
                           "center_lat": 34.014959683598164,
                           "center_lon": -118.4117215,
                           "order_by": "distance",
                           "company_uuid": "1234567",
                           "callback": "jQuery22407851157122881546_1596651612792",
                           "source": "agent % 20",
                           "website": "",
                           "source_display_name": "Windermere.com",
                           "_": ms_since_epoch()
                       },
                       headers={
                           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                           'cache-control': 'max-age=0',
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                       }).json()['data']['result_list']
    for x in res:
        yield x

def strip_extension(phone: str):
    return phone.split("x")[0]

def phone_number_extract(raw: str, which_index=0):
    split_phones = raw.split("/")
    try:
        return strip_extension(split_phones[which_index])
    except ValueError:
        return ""

def page_url_from_slug(slug: str):
    return "https://www.windermere.com/offices/" + slug

if __name__ == "__main__":
    crawler_domain = "windermere.com"
    SgCrawlerUsingHttpFun(
        crawler_domain=crawler_domain,
        transformer=DeclarativeTransformerAndFilter(
            pipeline=DeclarativePipeline(
                crawler_domain=crawler_domain,
                field_definitions=SSPFieldDefinitions(
                    locator_domain=ConstantField("https://windermere.com"),
                    page_url=MappingField(mapping=["url_slug"],value_transform=page_url_from_slug),
                    location_name=MappingField(mapping=['name'], is_required=False),
                    street_address=MultiMappingField(mapping=[["location", "address"], ["location", "address2"]]),
                    city=MappingField(mapping=["location", "city"]),
                    state=MappingField(mapping=["location", "state"]),
                    zipcode=MappingField(mapping=["location", "zip"], is_required=False),
                    country_code=MappingField(mapping=["location", "country_code"],is_required=False),
                    store_number=MappingField(mapping=["external_id"],part_of_record_identity=True),
                    phone=MappingField(mapping=["phone"], value_transform=phone_number_extract,is_required=False),
                    location_type=MappingField(mapping=["legal"], is_required=False),
                    latitude=MappingField(mapping=["location", "latitude"], is_required=False),
                    longitude=MappingField(mapping=["location", "longitude"], is_required=False),
                    hours_of_operation=MissingField(),
                    raw_address=MissingField()),
                fail_on_outlier=False)),
        fetch_raw_using=fetch_data,  # <-- Must yield raw dicts!
        make_http=lambda _: SgRequests(),
        data_writer=SgWriter()
    ).run()
```
