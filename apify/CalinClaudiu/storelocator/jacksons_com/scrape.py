from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgrequests import SgRequests
from sglogging import sglog
import json


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://jacksons.com/js/data/locations.js"
    # https://www.jacksons.com/js/data/locations.json
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"  # noqa
    }

    session = SgRequests()
    son = session.get(url, headers=headers)
    son = son.text
    son = '{"locs" :' + str(son).split("locations = ", 1)[1].rsplit(";")[0] + "}"
    son = json.loads(son)

    logzilla.info(f"Finished grabbing data!!")  # noqa

    for i in son["locs"]:
        yield i


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except Exception:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def scrape():
    url = "https://www.jacksons.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(
            mapping=["site_name"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        latitude=MappingField(
            mapping=["latitude"],
            part_of_record_identity=True,
        ),
        longitude=MappingField(
            mapping=["longitude"],
            part_of_record_identity=True,
        ),
        street_address=MappingField(
            mapping=["street"],
            part_of_record_identity=True,
        ),
        city=MappingField(
            mapping=["city"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        state=MappingField(
            mapping=["state"],
            part_of_record_identity=True,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=MappingField(
            mapping=["postal_code"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MissingField(),
        phone=MappingField(
            mapping=["main_phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MissingField(),
        hours_of_operation=MissingField(),
        location_type=MappingField(
            mapping=["amenities_list"],
            is_required=False,
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="jacksons.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
