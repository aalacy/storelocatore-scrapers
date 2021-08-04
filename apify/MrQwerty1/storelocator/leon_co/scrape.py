import json

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
from sgscrape.sgpostal import parse_address, International_Parser


def fetch_data(_, http: SgRequests):
    r = http.request(url="https://leon.co/all-restaurants/")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
    js = json.loads(text)["props"]["initialReduxState"]["data"]["restaurants"]
    for j in js:
        yield j


def get_street(full_adr):
    adr = parse_address(International_Parser(), full_adr)
    street = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    if len(street) < 5:
        street = full_adr.split(",")[0].strip()

    return street


def page_url_from_slug(slug: str):
    return f"https://leon.co/restaurants/{slug}"


if __name__ == "__main__":
    crawler_domain = "https://leon.co/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        SgCrawlerUsingHttpFun(
            crawler_domain=crawler_domain,
            transformer=DeclarativeTransformerAndFilter(
                pipeline=DeclarativePipeline(
                    crawler_domain=crawler_domain,
                    field_definitions=SSPFieldDefinitions(
                        locator_domain=ConstantField("https://leon.co/"),
                        page_url=MappingField(
                            mapping=["slug"],
                            value_transform=page_url_from_slug,
                            is_required=False,
                        ),
                        location_name=MappingField(mapping=["name"], is_required=False),
                        street_address=MappingField(
                            mapping=["locationDetails", "fullAddress"],
                            value_transform=get_street,
                        ),
                        city=MappingField(mapping=["locationDetails", "townOrCity"]),
                        state=MissingField(),
                        zipcode=MappingField(
                            mapping=["locationDetails", "postCode"], is_required=False
                        ),
                        country_code=ConstantField("GB"),
                        store_number=MissingField(),
                        phone=MappingField(
                            mapping=["contactDetails", "phoneNumber"], is_required=False
                        ),
                        location_type=MappingField(mapping=["type"], is_required=False),
                        latitude=MappingField(
                            mapping=["geoLocation", "lat"], is_required=False
                        ),
                        longitude=MappingField(
                            mapping=["geoLocation", "lng"], is_required=False
                        ),
                        hours_of_operation=MissingField(),
                        raw_address=MappingField(
                            mapping=["locationDetails", "fullAddress"]
                        ),
                    ),
                    fail_on_outlier=False,
                )
            ),
            fetch_raw_using=fetch_data,
            make_http=lambda _: SgRequests(),
            data_writer=writer,
        ).run()
