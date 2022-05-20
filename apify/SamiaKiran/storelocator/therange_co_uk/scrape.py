import json
import ssl
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import tenacity
import time

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


website = "therange_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.therange.co.uk"
MISSING = SgRecord.MISSING


@tenacity.retry(wait=tenacity.wait_fixed(3))
def get_with_retry(driver, url):
    driver.get(url)
    time.sleep(7)
    return driver.page_source, driver


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 2:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    x = 0
    while True:
        x = x + 1
        class_name = "storelist"
        url = "https://www.therange.co.uk/stores/"
        if x == 1:
            driver = get_driver(url, class_name)
        else:
            driver = get_driver(url, class_name, driver=driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.find("ul", {"id": "storelist"}).findAll("li")
        log.info(f"Total Stores: {len(loclist)}")
        if len(loclist) == 0:
            continue
        else:
            break

    for loc in loclist:
        page_url = "https://www.therange.co.uk" + loc.find("a")["href"]
        log.info(page_url)
        response, driver_page_url = get_with_retry(driver, page_url)
        temp = json.loads(
            response.split('<script type="application/ld+json">')[1].split("</script>")[
                0
            ]
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
                + hour["dayOfWeek"].replace("http://schema.org/", "")
                + " "
                + hour["opens"]
                + "-"
                + hour["closes"]
            )
        try:
            driver_page_url.switch_to.frame(0)
            geo_link = driver.find_element(
                By.XPATH, '//div[@class="google-maps-link"]/a'
            ).get_attribute("href")

            log.info(f"GEO LINK: {geo_link}")
            latitude = geo_link.split("ll=")[1].split(",")[0].strip()
            longitude = geo_link.split("ll=")[1].split(",")[1].split("&")[0].strip()
        except:
            latitude = MISSING
            longitude = MISSING

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
            latitude=latitude,
            longitude=longitude,
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
