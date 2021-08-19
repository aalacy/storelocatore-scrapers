from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog


from sgrequests import SgRequests

import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://sheets.googleapis.com/v4/spreadsheets/1Lsd18ghPtfinq8QnpU0_-UQYBQuUZK55ECbOPaE7_UU/values/Locations_Live!A:Z?key=AIzaSyA7kW9-Yu45nh14JgE_eabPX44ABs6rVpM&callback=jQuery311013815880869144226_1612115427721&_=1612115427722"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = session.get(url, headers=headers).text
    son = json.loads("{" + soup.split("({", 1)[1].rsplit(");", 1)[0])
    son = son["values"]
    son.pop(0)
    for i in son:
        if "enske" in i[0]:
            yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.penskeautomotive.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=[8]),
        location_name=MappingField(mapping=[0]),
        latitude=MissingField(),
        longitude=MissingField(),
        street_address=MappingField(mapping=[2]),
        city=MappingField(mapping=[3]),
        state=MappingField(mapping=[4]),
        zipcode=MappingField(mapping=[6]),
        country_code=MappingField(mapping=[5]),
        phone=MappingField(mapping=[7]),
        store_number=MissingField(),
        hours_of_operation=ConstantField("<INACCESSIBLE>"),
        location_type=MappingField(mapping=[1]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
