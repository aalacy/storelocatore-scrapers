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


def fetch_data(_, http: SgRequests):
    res = http.request(
        url="https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=answers-jonesbootmaker&api_key=9d200ab7c8620cc20297f7dbfd870b45&v=20190101&version=PRODUCTION&locale=en_GB&input=&verticalKey=location&limit=50&offset=0&facetFilters={}&queryTrigger=initialize&sessionTrackingEnabled=true&sortBys=[]&referrerPageUrl=&source=STANDARD&jsLibVersion=v1.8.6",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
    ).json()["response"]["results"]
    for x in res:
        yield x


def get_hours(intervals):
    _tmp = []
    for day, interval in intervals.items():
        if interval.get("isClosed"):
            _tmp.append(f"{day.capitalize()}: Closed")
            continue

        start = interval["openIntervals"][0]["start"]
        end = interval["openIntervals"][0]["end"]
        _tmp.append(f"{day.capitalize()}: {start} - {end}")

    return ";".join(_tmp)


if __name__ == "__main__":
    crawler_domain = "jonesbootmaker.com"
    with SgWriter() as writer:
        SgCrawlerUsingHttpFun(
            crawler_domain=crawler_domain,
            transformer=DeclarativeTransformerAndFilter(
                pipeline=DeclarativePipeline(
                    crawler_domain=crawler_domain,
                    field_definitions=SSPFieldDefinitions(
                        locator_domain=ConstantField("https://jonesbootmaker.com"),
                        page_url=MappingField(mapping=["data", "website"]),
                        location_name=MappingField(
                            mapping=["data", "name"], is_required=False
                        ),
                        street_address=MappingField(
                            mapping=["data", "address", "line1"]
                        ),
                        city=MappingField(mapping=["data", "address", "city"]),
                        state=MissingField(),
                        zipcode=MappingField(
                            mapping=["data", "address", "postalCode"], is_required=False
                        ),
                        country_code=MappingField(
                            mapping=["data", "address", "countryCode"],
                            is_required=False,
                        ),
                        store_number=MappingField(
                            mapping=["data", "id"], part_of_record_identity=True
                        ),
                        phone=MappingField(
                            mapping=["data", "mainPhone"], is_required=False
                        ),
                        location_type=MissingField(),
                        latitude=MappingField(
                            mapping=["data", "yextDisplayCoordinate", "latitude"],
                            is_required=False,
                        ),
                        longitude=MappingField(
                            mapping=["data", "yextDisplayCoordinate", "longitude"],
                            is_required=False,
                        ),
                        hours_of_operation=MappingField(
                            mapping=["data", "hours"], raw_value_transform=get_hours
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
