from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import re

logger = SgLogSetup().get_logger("roundtablepizza")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://roundtablepizza.com/"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=100,
    max_search_results=10,
)


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        url = f"https://ordering.roundtablepizza.com/Site/rtp/Locations?isFrame=False&lat={lat}&lon={lng}&IsInit=false"
        locations = bs(
            session.get(url, headers=headers, timeout=15).text, "lxml"
        ).select("section > div.locationInfo")
        total += len(locations)
        for _ in locations:
            store = dict()
            store["store_number"] = _["data-companyseq"]
            store["location_name"] = _.select_one("a.locationName").text
            store["page_url"] = _.select_one("a.locationName")["href"]
            addr = list(_.select("div.locationInfoBox > div")[1].stripped_strings)
            store["street_address"] = addr[0]
            store["city"] = addr[1].split(",")[0].strip()
            store["state"] = addr[1].split(",")[1].strip().split(" ")[0].strip()
            store["zip_postal"] = addr[1].split(",")[1].strip().split(" ")[-1].strip()
            store["phone"] = addr[-1]
            store["hours_of_operation"] = ""
            hours = _.find("span", string=re.compile(r"open", re.IGNORECASE))
            if hours:
                store["hours_of_operation"] = hours.text.strip()
            coord = (
                _.select_one("a.locationCenter")["onclick"]
                .split("(")[1]
                .split(")")[0]
                .split(",")
            )
            store["latitude"] = float(coord[0].strip()[1:-1])
            store["longitude"] = float(coord[1].strip()[1:-1])
            search.found_location_at(
                store["latitude"],
                store["longitude"],
            )
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        if len(locations):
            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip_postal"],
        ),
        country_code=sp.ConstantField("US"),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["store_number"],
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
