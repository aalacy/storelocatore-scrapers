import time
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "toalsbet.com"

website = "http://www.toalsbet.com/shop-locator/"

MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_like_js(start_url, driver):
    stores = []
    data = driver.execute_async_script(
        f"""
    var done = arguments[0]
    fetch("{start_url}", {{
    "credentials": "include",
    "headers": {{
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }},
    "referrer": "https://www.toalsbet.com/shop-locator/",
    "method": "GET",
    "mode": "cors"
    }})
    .then(res => res.json())
    .then(data => done(data))
    """
    )

    stores = data["storeLocations"]
    return stores


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    with SgChrome(
        is_headless=True,
        user_agent=user_agent,
        executable_path=ChromeDriverManager().install(),
    ) as driver:
        log.info("initiating Driver")
        driver.get(website)
        time.sleep(30)
        start_url = "https://www.toalsbet.com/resources/store_locations.lst"
        time.sleep(15)
        log.info(f"Now crawling {start_url}")
        stores = fetch_like_js(start_url, driver)

        log.info(f"Total stores = {len(stores)}")
        store_number = MISSING
        location_type = MISSING
        hours_of_operation = MISSING
        country_code = "UK"

        for store in stores:
            location_name = store["name"]
            raw_address = store["address"]
            street_address, city, state, zip_postal = get_address(raw_address)
            phone = MISSING
            if "tel" in store:
                phone = store["tel"].split(",")[0].strip()
            latitude = store["lat"]
            longitude = store["lon"]

            yield SgRecord(
                locator_domain=DOMAIN,
                store_number=store_number,
                page_url=website,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
