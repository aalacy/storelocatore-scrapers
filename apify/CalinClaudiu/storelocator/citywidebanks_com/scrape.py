from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from bs4 import BeautifulSoup as b4


from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.citywidebanks.com/node.json?type=locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()

    for i in son["list"]:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def nice_featuers(x):
    return ", ".join(x)


def soupy_hours(x):
    try:
        return "; ".join(list(b4(x, "lxml").stripped_strings))
    except Exception:
        return x


def scrape():
    url = "https://www.citywidebanks.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["url"],
        ),
        location_name=sp.MappingField(
            mapping=["title"],
        ),
        latitude=sp.MappingField(
            mapping=["field_location_street_address", "lat"],
        ),
        longitude=sp.MappingField(
            mapping=["field_location_street_address", "lon"],
        ),
        street_address=sp.MappingField(
            mapping=["field_street_address", "thoroughfare"],
        ),
        city=sp.MappingField(
            mapping=["field_street_address", "locality"],
        ),
        state=sp.MappingField(
            mapping=["field_street_address", "administrative_area"],
        ),
        zipcode=sp.MappingField(
            mapping=["field_street_address", "postal_code"],
        ),
        country_code=sp.MappingField(
            mapping=["field_street_address", "country"],
        ),
        phone=sp.MappingField(
            mapping=["field_phone_number"],
        ),
        store_number=sp.MappingField(
            mapping=["nid"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["field_lobby_hours", "value"], value_transform=soupy_hours
        ),
        location_type=sp.MappingField(
            mapping=["field_bank_features"], raw_value_transform=nice_featuers
        ),
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
