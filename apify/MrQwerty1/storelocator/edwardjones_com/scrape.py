from typing import Iterable

from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import (
    ConstantField,
    MappingField,
    MissingField,
    SimpleScraperPipeline,
)


def fetch_data() -> Iterable[dict]:
    with SgRequests() as http:
        for i in range(1, 5000):
            res = http.request(
                url=f"https://www.edwardjones.com/api/financial-advisor/results?q=75022&distance=5000&page={i}",
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
            ).json()["results"]

            for x in res:
                yield x

            if len(res) < 15:
                break


def get_page_url(url):
    return f"https://www.edwardjones.com{url}"


def get_street(adr):
    return ",".join(adr.split(",")[:-2])


def get_postal(adr):
    return adr.split()[-1]


def get_state(adr):
    return adr.split()[-2]


def get_city(adr):
    return adr.split(",")[-2].strip()


if __name__ == "__main__":
    crawler_domain = "edwardjones.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField("https://www.edwardjones.com/"),
        page_url=MappingField(mapping=["faUrl"], value_transform=get_page_url),
        location_name=MappingField(mapping=["faName"], is_required=False),
        street_address=MappingField(mapping=["address"], value_transform=get_street),
        city=MappingField(mapping=["address"], value_transform=get_city),
        state=MappingField(mapping=["address"], value_transform=get_state),
        zipcode=MappingField(mapping=["address"], value_transform=get_postal),
        country_code=ConstantField("US"),
        store_number=MappingField(mapping=["faEntityId"], part_of_record_identity=True),
        phone=MappingField(mapping=["phone"], is_required=False),
        location_type=MissingField(),
        latitude=MappingField(
            mapping=["lat"],
            is_required=False,
        ),
        longitude=MappingField(
            mapping=["lon"],
            is_required=False,
        ),
        hours_of_operation=MissingField(),
        raw_address=MappingField(mapping=["address"]),
    )

    SimpleScraperPipeline(
        scraper_name=crawler_domain,
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        fail_on_outlier=False,
    ).run()
