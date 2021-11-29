from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt
import ssl
from lxml import html
import time
from sgpostal.sgpostal import parse_address_intl
from selenium.webdriver.common.action_chains import ActionChains


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("soibrow_com")
MISSING = SgRecord.MISSING
DOMAIN = "soibrow.com"
LOCATION_URL = "https://www.soibrow.com/locations"

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"


@retry(stop=stop_after_attempt(3))
def get_response(http, urlnum, url):
    logger.info(f"[{urlnum}] Pulling the data from: {url}")
    r = http.get(url, headers=HEADERS)
    if r.status_code == 200:
        logger.info(f"HTTP Status Code: {r.status_code}")
        return r
    raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def get_driver(url, class_name, timeout, driver=None):
    if driver is not None:
        driver.quit()
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
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(f"Fix the issue {url}:(")
            continue
    return driver


def get_phone(storenum):
    class_name = "dmGeoMLocItem"
    timeout = 20
    driver = get_driver(LOCATION_URL, class_name, timeout)
    location_xpath = (
        f'//li[contains(@class, "dmGeoMLocItem") and contains(@geoid, "{storenum}")]'
    )
    logger.info(f"location xpath: {location_xpath}")
    WebDriverWait(driver, 40).until(
        EC.element_to_be_clickable((By.XPATH, location_xpath))
    )
    element = driver.find_element_by_xpath(location_xpath)
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    driver.find_element_by_xpath(location_xpath).click()
    logger.info("Location Link Clicked")
    time.sleep(5)
    selphone = html.fromstring(driver.page_source, "lxml")
    phone_xpath = '//a[contains(@href, "tel:")]/@phone'
    phone = selphone.xpath(phone_xpath)
    phone = "".join(phone)
    phone = phone if phone else MISSING
    logger.info(f"Phone: {phone} for {storenum}")
    return phone


def fetch_records(http: SgRequests):
    r = get_response(http, 0, LOCATION_URL)
    sel = html.fromstring(r.text, "lxml")
    storenumber = sel.xpath('//li[contains(@class, "dmGeoMLocItem")]/@geoid')
    uls = sel.xpath('//ul[contains(@class, "dmGeoMLocList")]/li')
    for idx, ul in enumerate(uls[0:]):
        ln = "".join(ul.xpath('./a/span[@class="dmGeoMLocItemTitle"]/text()'))
        ln = ln if ln else MISSING
        logger.info(f"[{idx}] ln: {ln}")
        radd = ul.xpath('./a/span[@class="dmGeoMLocItemDetails"]/text()')[0]

        sn = storenumber[idx]
        pai = parse_address_intl(radd)
        sta = pai.street_address_1
        sta = sta if sta is not None else MISSING

        c = pai.city
        c = c if c is not None else MISSING

        s = pai.state
        s = s if s is not None else MISSING

        zp = pai.postcode
        zp = zp if zp is not None else MISSING

        cc = pai.country
        cc = cc if cc is not None else MISSING
        phone = get_phone(sn)
        item = SgRecord(
            page_url=LOCATION_URL,
            locator_domain=DOMAIN,
            location_name=ln,
            street_address=sta,
            city=c,
            state=s,
            zip_postal=zp,
            country_code=cc,
            store_number=sn,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=MISSING,
            raw_address=radd if radd else MISSING,
        )
        yield item


def scrape():
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
