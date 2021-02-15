from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://apps.abf.com/api/abf-network/stations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()

    for i in son["stations"]:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://arcb.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["stationNumber"],
            value_transform=lambda x: "https://apps.abf.com/api/abf-network/stations/"
            + str(x)
            + "/detailed",
        ),
        location_name=sp.MappingField(mapping=["title"], is_required=False),
        latitude=sp.MissingField(),
        longitude=sp.MissingField(),
        street_address=sp.MappingField(mapping=["location", "address"]),
        city=sp.MappingField(mapping=["location", "city"]),
        state=sp.MappingField(mapping=["location", "state"]),
        zipcode=sp.MappingField(mapping=["location", "zip"]),
        country_code=sp.MappingField(
            mapping=["location", "country"], is_required=False
        ),
        phone=sp.MappingField(mapping=["customerServicePhone"], is_required=False),
        store_number=sp.MappingField(mapping=["stationNumber"]),
        hours_of_operation=sp.MappingField(
            mapping=["status"],
            value_transform=lambda x: "<MISSING>"
            if x == "Active"
            else "Possibly Closed",
        ),
        location_type=sp.MappingField(mapping=["airlineCode"], is_required=False),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
