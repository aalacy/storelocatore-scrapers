from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("roundtablepizza")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://roundtablepizza.com/"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=None,
)


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    with SgChrome() as driver:
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
                store["location_name"] = _.select_one(".locationName").text
                store["page_url"] = (
                    _.select_one("a.locationName")["href"]
                    if _.select_one("a.locationName")
                    else "<MISSING>"
                )
                addr = list(_.select("div.locationInfoBox > div")[1].stripped_strings)
                store["street_address"] = addr[0]
                store["city"] = addr[1].split(",")[0].strip()
                store["state"] = addr[1].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = addr[1].split(",")[1].strip().split(" ")[-1].strip()
                store["zip_postal"] = zip_postal if _phone(zip_postal) else "<MISSING>"
                store["phone"] = addr[-1] if _phone(addr[-1]) else "<MISSING>"
                store["hours_of_operation"] = "<MISSING>"
                if (
                    store["page_url"] != "<MISSING>"
                    and store["page_url"] != "https://pinol03.intouchposonline.com"
                ):
                    logger.info(f"[url] {store['page_url']}")
                    try:
                        sp1 = bs(
                            session.get(
                                store["page_url"], headers=headers, timeout=15
                            ).text,
                            "lxml",
                        )
                        hours = [
                            ": ".join(hh.stripped_strings)
                            for hh in sp1.select("#openHours ul li")
                        ]
                        if sp1.select_one("span.phone"):
                            store["phone"] = sp1.select_one("span.phone").text.strip()
                        if not hours:
                            driver.get(store["page_url"])
                            sp1 = bs(driver.page_source, "lxml")
                            store["zip_postal"] = sp1.select_one(
                                "span.zip"
                            ).text.strip()
                            for hh in sp1.select("div.dayHoursContainer div.dayHours"):
                                hours.append(
                                    f"{hh.select_one('span.startDayContainer').text.strip()}: {''.join(hh.select_one('span.timeContainer').stripped_strings)}"
                                )
                    except:
                        pass

                    store["hours_of_operation"] = (
                        "; ".join(hours).replace("–", "-") or "<MISSING>"
                    )

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
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

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
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
            part_of_record_identity=True,
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
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["store_number"],
            part_of_record_identity=True,
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
