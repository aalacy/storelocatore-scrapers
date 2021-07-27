from sgcrawler.sgcrawler_fun import SgCrawlerUsingHttpFun
from sgcrawler.helper_definitions import (
    DeclarativeTransformerAndFilter,
    DeclarativePipeline,
)
from sgrequests import SgRequests
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.simple_scraper_pipeline import (
    SSPFieldDefinitions,
    ConstantField,
    MappingField,
    MissingField,
)
from sgscrape.sgwriter import SgWriter


def fetch_data(_, http: SgRequests):

    res = http.request(
        url="https://api.freshop.com/1/stores?app_key=riesbeck&has_address=true&is_selectable=true&limit=100&token=c5bbce0aec6a506c9e6b9c53d71fc123",
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        },
    ).json()["items"]
    for x in res:
        yield x


def strip_extension(phone: str):
    return phone.split("\n")[0]


if __name__ == "__main__":
    crawler_domain = "riesbeckfoods.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        SgCrawlerUsingHttpFun(
            crawler_domain=crawler_domain,
            transformer=DeclarativeTransformerAndFilter(
                pipeline=DeclarativePipeline(
                    crawler_domain=crawler_domain,
                    field_definitions=SSPFieldDefinitions(
                        locator_domain=ConstantField("https://www.riesbeckfoods.com"),
                        page_url=MappingField(
                            mapping=["url"]
                            or "https://www.riesbeckfoods.com/my-store/store-locator"
                        ),
                        location_name=MappingField(mapping=["name"], is_required=False),
                        street_address=MappingField(mapping=["address_1"]),
                        city=MappingField(mapping=["city"]),
                        state=MappingField(mapping=["state"]),
                        zipcode=MappingField(
                            mapping=["postal_code"], is_required=False
                        ),
                        country_code=ConstantField("USA"),
                        store_number=MappingField(
                            mapping=["store_number"], part_of_record_identity=True
                        ),
                        phone=MappingField(
                            mapping=["phone_md"],
                            value_transform=strip_extension,
                            is_required=False,
                        ),
                        location_type=MissingField(),
                        latitude=MappingField(mapping=["latitude"], is_required=False),
                        longitude=MappingField(
                            mapping=["longitude"], is_required=False
                        ),
                        hours_of_operation=MappingField(
                            mapping=["hours_md"], is_required=False
                        ),
                        raw_address=MissingField(),
                    ),
                    fail_on_outlier=False,
                )
            ),
            fetch_raw_using=fetch_data,
            make_http=lambda _: SgRequests(),
            data_writer=SgWriter(),
        ).run()
