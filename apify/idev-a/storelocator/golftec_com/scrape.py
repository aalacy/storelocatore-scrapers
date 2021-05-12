from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import json

logger = SgLogSetup().get_logger("comerica_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.golftec.com"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
    max_radius_miles=None,
    max_search_results=None,
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
        url = f"https://wcms.golftec.com/loadmarkers_6.php?thelong={lng}&thelat={lat}&georegion=North+America&pagever=prod&maptype=closest10"
        locations = session.get(url, headers=headers, timeout=15).json()
        total += len(locations)
        if "centers" in locations:
            for _ in locations["centers"]:
                page_url = f"{locator_domain}{_['link']}"
                soup = bs(
                    session.get(page_url, headers=headers, timeout=15).text, "lxml"
                )
                store = json.loads(
                    soup.find("script", type="application/ld+json").string.strip()
                )
                search.found_location_at(
                    store["geo"]["latitude"],
                    store["geo"]["longitude"],
                )
                store["lat"] = store["geo"]["latitude"]
                store["lng"] = store["geo"]["longitude"]
                store["street"] = store["address"]["streetAddress"]
                store["city"] = store["address"]["addressLocality"]
                store["state"] = store["address"]["addressRegion"]
                store["zip_postal"] = store["address"]["postalCode"]
                store["country"] = store["address"]["addressCountry"]
                hours = []
                for hh in store["openingHoursSpecification"]:
                    day = hh["dayOfWeek"].split("/")[-1]
                    time = "closed"
                    if "opens" in hh and "closes" in hh:
                        time = f"{hh['opens']}-{hh['closes']}"
                    hours.append(f"{day}: {time}")
                store["hours"] = "; ".join(hours) or "<MISSING>"
                yield store
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(
            mapping=["street"],
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
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["telephone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(
            mapping=["@type"],
        ),
        store_number=sp.MissingField(),
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
