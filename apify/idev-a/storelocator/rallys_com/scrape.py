from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import SgLogSetup
import us

logger = SgLogSetup().get_logger("rallys")

headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

locator_domain = "https://www.rallys.com/"


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    total = 0
    for state in us.states.STATES:
        logger.info(("Pulling Geo Code %s..." % state.name))
        url = f"https://locations.rallys.com/search?region={state.abbr}&country=US&qp={state.name},%20United%20States&l=en"
        locations = session.get(url, headers=headers, timeout=15).json()
        total += len(locations)
        if "response" in locations:
            for _ in locations["response"]["entities"]:
                store = _["profile"]
                try:
                    if "displayCoordinate" in store:
                        store["lat"] = store["displayCoordinate"]["lat"]
                        store["lng"] = store["displayCoordinate"]["long"]
                    if "geocodedCoordinate" in store:
                        store["lat"] = store["geocodedCoordinate"]["lat"]
                        store["lng"] = store["geocodedCoordinate"]["long"]
                    elif "cityCoordinate" in store:
                        store["lat"] = store["cityCoordinate"]["lat"]
                        store["lng"] = store["cityCoordinate"]["long"]
                except:
                    import pdb

                    pdb.set_trace()
                store["street"] = store["address"]["line1"]
                if store["address"]["line2"]:
                    store["street"] += " " + store["address"]["line2"]
                if store["address"]["line3"]:
                    store["street"] += " " + store["address"]["line3"]
                store["city"] = store["address"]["city"]
                store["state"] = store["address"]["region"]
                store["zip_postal"] = store["address"]["postalCode"]
                store["country"] = store["address"]["countryCode"]
                store["phone"] = store["mainPhone"]["display"]
                hours = []
                for hh in store["hours"]["normalHours"]:
                    time = "closed"
                    if not hh["isClosed"]:
                        time = (
                            f"{hh['intervals'][0]['start']}-{hh['intervals'][0]['end']}"
                        )
                    hours.append(f"{hh['day']}: {time}")
                store["hours"] = "; ".join(hours) or "<MISSING>"
                yield store
            logger.info(f"[{state.abbr}] found: {len(locations)} | total: {total}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["websiteUrl"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["c_storeName"],
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
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        store_number=sp.MissingField(),
        location_type=sp.MissingField(),
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
