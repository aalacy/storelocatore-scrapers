import time
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from w3lib.url import add_or_replace_parameter
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "yogurt-land.com"
website = "https://www.yogurt-land.com/locations"

MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_like_js(start_url, driver):
    data = driver.execute_async_script(
        f"""
    var done = arguments[0]
    fetch("{start_url}", {{
    "credentials": "include",
    "headers": {{
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "X-Api-Key": "QeKEiECfiACR",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }},
    "referrer": "https://www.yogurt-land.com/locations",
    "method": "GET",
    "mode": "cors"
    }})
    .then(res => res.json())
    .then(data => done(data))
    """
    )

    return data


def fetch_data():
    with SgChrome(
        is_headless=True,
        user_agent=user_agent,
        executable_path=ChromeDriverManager().install(),
    ) as driver:
        log.info("initiating Driver")
        driver.get(website)
        start_url = "https://www.yogurt-land.com/api/1.1/locations/search.json?app_mode=1&include-html=1&location-selector-type=&zip-code-or-address-hidden=&page=1&lng=&lat=&favorite-location=0&search="
        time.sleep(15)
        log.info("Now crawling page#1")
        data = fetch_like_js(start_url, driver)
        locs = data["locations"]
        next_page = data["has_more"]

        while next_page:
            page_num = str(int(data["page"]) + 1)
            log.info(f"Now crawling page#{page_num}")
            next_page_url = add_or_replace_parameter(start_url, "page", page_num)
            data = fetch_like_js(next_page_url, driver)
            locs += data["locations"]
            log.info(f"Counting locations : {len(locs)}")
            next_page = data["has_more"]

        log.info(f"Total locations to be pulled: {len(locs)}")
        for loc in locs:
            store_url = "https://www.yogurt-land.com/locations/view/{}/{}".format(
                loc["Location"]["id"], loc["Location"]["name"].replace(" & ", "-")
            )
            store_url = store_url
            location_name = loc["Location"]["name"]
            street_address = loc["Location"]["address"]
            if loc["Location"]["address_2"]:
                street_address += ", " + loc["Location"]["address_2"]

            city = loc["Location"]["city"]

            state = loc["Location"]["state_code"]

            zip_code = loc["Location"]["postal_code"]

            country_code = loc["Location"]["country_code"]

            if country_code not in ["US", "CA"]:
                continue

            store_number = loc["Location"]["id"]

            phone = loc["Location"]["phone"]

            location_type = MISSING

            latitude = loc["Location"]["latitude"]

            longitude = loc["Location"]["longitude"]

            hours_of_operation = loc["Location"]["formatted_hours"]
            hours_of_operation = (
                hours_of_operation.replace("<br />", " ")
                if hours_of_operation
                else MISSING
            )

            yield SgRecord(
                locator_domain=DOMAIN,
                store_number=store_number,
                page_url=store_url,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_code,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Crawling Started")
    count = 0
    start = time.time()
    result = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
