import json
import tenacity
from sglogging import sglog
from bs4 import BeautifulSoup
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


@tenacity.retry(wait=tenacity.wait_fixed(3))
def get_with_retry(driver, url):
    driver.get(url)
    driver.set_page_load_timeout(20)
    return driver.page_source


session = SgRequests()
website = "therange_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

DOMAIN = "https://www.therange.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        with SgChrome(
            executable_path=ChromeDriverManager().install(),
            is_headless=True,
            user_agent=user_agent,
        ) as driver:
            url = "https://www.therange.co.uk/stores/"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            loclist = soup.find("ul", {"id": "storelist"}).findAll("li")
            for loc in loclist:
                page_url = "https://www.therange.co.uk" + loc.find("a")["href"]
                log.info(page_url)
                response = get_with_retry(driver, page_url)
                temp = json.loads(
                    response.split('<script type="application/ld+json">')[1].split(
                        "</script>"
                    )[0]
                )
                location_name = temp["name"]
                phone = temp["telephone"]
                address = temp["address"]
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                hour_list = temp["openingHoursSpecification"]
                hours_of_operation = ""
                for hour in hour_list:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + hour["dayOfWeek"]
                        + " "
                        + hour["opens"]
                        + "-"
                        + hour["closes"]
                    )
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
