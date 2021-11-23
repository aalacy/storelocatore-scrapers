# Writing Records to `data.csv`

#### Library version:

```
sgscrape>=0.1.8
```

## Introducing `SgWriter`

- Historically, crawl-writers had to manage writing raw records to the `data.csv` file, alongside many other concerns.
- `SgRecord`, `SgRecordID`, `SgRecordDeduper` and `SgWriter` were created to solve many such concerns:
  - How to define a proper encoding for the file?
  - Make sure that the headers and records align.
  - How to define a record's ID, and efficiently and correctly deduplicate records?
  - And now: How to integrate with the pause/resume functionality?
- (Note that [SimpleScraperPipeline](./declarative_pipeline.md) is an even easier way, and is highly recommended!)
- Make sure that you read the [section about records and unique identity](./records_and_id.md) before continuing.

## `SgWriter` features:

- Uses the proper file encoding.
- Deduplicates records when you supply an `SgRecordDeduper`.
  - This should be adhered to 99% of the time.
  - In _very special situations_, you can omit record deduplication, if you absolutely must perform it separately.
- Reads any existing `data.csv` file, and adds its records to the de-duplicator. (See [Pause/Resume functionality](./pause_resume.md))

## `SgWriter` in Action:

- Using `SgWriter` is easy:

```python
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

def fetch_data(sgw: SgWriter):
    sgw.write_row(SgRecord(page_url="123.com/1", store_number='', latitude=3.1415, longitude=3.1415))
    sgw.write_row(SgRecord(raw={'page_url':"123.com/2", 'store_number': ''}))
    sgw.write_row(SgRecord(raw={'page_url':"123.com/3", 'store_number': ''}))
with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
```
