from lxml import html
from sgcrawler.sgcrawler_fun import SgCrawlerUsingHttpFun
from sgcrawler.helper_definitions import (
    DeclarativeTransformerAndFilter,
    DeclarativePipeline,
)
from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import (
    SSPFieldDefinitions,
    ConstantField,
    MappingField,
    MissingField,
)
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(_, http: SgRequests):
    r = http.request(
        url="https://www.firstunitedbank.com/q2_map/ajax/get-location-data/1"
    )
    js = r.json()["locations"]

    for j in js:
        yield j


def get_type(types: list):
    return types.pop(0)


def get_hours(source: str):
    _tmp = []
    tree = html.fromstring(source)
    tr = tree.xpath("//tr[./td[1]/strong]")
    for t in tr:
        day = "".join(t.xpath("./td[1]/strong/text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
        if "N/A" in time:
            continue
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp)


if __name__ == "__main__":
    crawler_domain = "firstunitedbank.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        SgCrawlerUsingHttpFun(
            crawler_domain=crawler_domain,
            transformer=DeclarativeTransformerAndFilter(
                pipeline=DeclarativePipeline(
                    crawler_domain=crawler_domain,
                    field_definitions=SSPFieldDefinitions(
                        locator_domain=ConstantField(
                            "https://www.firstunitedbank.com/"
                        ),
                        page_url=MappingField(
                            mapping=["url"],
                            is_required=False,
                        ),
                        location_name=MappingField(mapping=["name"], is_required=False),
                        street_address=MappingField(
                            mapping=["address"], is_required=False
                        ),
                        city=MappingField(mapping=["city"], is_required=False),
                        state=MappingField(mapping=["state"], is_required=False),
                        zipcode=MappingField(mapping=["zip"], is_required=False),
                        country_code=ConstantField("US"),
                        store_number=MissingField(),
                        phone=MappingField(mapping=["phone"], is_required=False),
                        location_type=MappingField(
                            mapping=["type"],
                            raw_value_transform=get_type,
                            is_required=False,
                        ),
                        latitude=MappingField(mapping=["lat"], is_required=False),
                        longitude=MappingField(mapping=["long"], is_required=False),
                        hours_of_operation=MappingField(
                            mapping=["hours"],
                            value_transform=get_hours,
                            is_required=False,
                        ),
                        raw_address=MissingField(),
                    ),
                    fail_on_outlier=False,
                )
            ),
            fetch_raw_using=fetch_data,
            make_http=lambda _: SgRequests(),
            data_writer=writer,
        ).run()
