import ssl
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support import expected_conditions as EC


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


website = "genesishcc_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://genesishcc.com"
MISSING = SgRecord.MISSING


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

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    x = 0
    while True:
        x = x + 1
        class_name = "nano"
        url = "https://genesishcc.com/findlocations/"
        if x == 1:
            driver = get_driver(url, class_name)
        else:
            driver = get_driver(url, class_name, driver=driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.findAll("div", {"class": "nano"})
        if len(loclist) == 0:
            continue
        else:
            break
    for loc in loclist:
        page_url = DOMAIN + loc.find("a")["href"]
        log.info(page_url)
        location_name = loc.find("div", {"class": "cI-title"}).text
        raw_address = (
            loc.find("div", {"class": "cI-address"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )

        # Parse the address
        pa = parse_address_intl(raw_address)

        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        zip_postal = zip_postal.strip() if zip_postal else MISSING
        street_address = street_address.replace("Rating Not Currently Available", "")
        try:
            driver.get(page_url)
        except:
            driver.get(page_url)
            WebDriverWait(driver, 30)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            phone = (
                soup.select_one("a[href*=tel]")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Phone: ", "")
            )
        except:
            phone = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code="US",
            store_number=MISSING,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=MISSING,
            raw_address=raw_address,
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
