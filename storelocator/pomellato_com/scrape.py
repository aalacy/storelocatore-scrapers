from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("pomellato")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pomellato.com"
page_url = "https://www.pomellato.com/en_intl/store-locator"
base_url = (
    "https://www.pomellato.com/api/ext/store-locator/geolocation/{}/{}?storeCode=en_us"
)

# SearchableCountries.WITH_ZIPCODE_AND_COORDS
search = DynamicGeoSearch(
    country_codes=SearchableCountries.WITH_ZIPCODE_AND_COORDS,
    granularity=Grain_4(),
)


def _p(val):
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
    country_list = []
    with SgChrome() as driver:
        driver.get(page_url)
        link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'pointer m0 inline-flex')]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", link)
        time.sleep(2)
        country_list = [
            cc["href"].split("_")[-1]
            for cc in bs(driver.page_source, "lxml").select("div.country-list a")[:-2]
        ]
    maxZ = search.items_remaining()
    total = 0
    logger.info("country list" + ",".join(country_list))
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        if search.current_country() not in country_list:
            continue
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        locations = session.get(base_url.format(lat, lng), headers=_headers).json()
        if type(locations) == dict and locations.get("code") == 400:
            continue
        total += len(locations)
        for store in locations:
            if "boutique" not in store["storeType"]:
                continue
            store["lat"] = store["location"]["lat"]
            store["lng"] = store["location"]["lon"]
            addr = parse_address_intl(store["street"])
            store["street_address"] = store["street"].split(",")[0].strip()
            store["state"] = addr.state
            if not store["state"]:
                store["state"] = "<MISSING>"
            store["zip_postal"] = addr.postcode
            if not store["zip_postal"]:
                store["zip_postal"] = "<MISSING>"
            store["hours_of_operation"] = (
                "; ".join(store.get("hours", [])) or "<MISSING>"
            )
            if (
                "notre boutique est temporairement"
                in store["hours_of_operation"].lower()
            ):
                store["hours_of_operation"] = "temporarily closed"
            store["phone"] = (
                store["phones"][0] if store.get("phones", []) else "<MISSING>"
            )
            store["type"] = ",".join(store["storeType"])
            store["page_url"] = page_url
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["page_url"],
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
            part_of_record_identity=True,
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
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MappingField(
            mapping=["type"],
        ),
        store_number=sp.MappingField(
            mapping=["source_code"],
        ),
        raw_address=sp.MappingField(
            mapping=["street"],
        ),
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
