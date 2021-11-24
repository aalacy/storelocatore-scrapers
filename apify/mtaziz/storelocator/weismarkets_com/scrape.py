from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
from lxml import html


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


LOCATION_URL = "https://www.weismarkets.com/stores/?coordinates=40.539711620149,-75.733030850299&zoom=10"
MAX_WORKERS = 10
DOMAIN = "weismarkets.com"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("weismarkets_com")

headers = {
    "accept": "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "MMozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


def get_driver(url, class_name, timeout, driver=None):
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
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 3:
                raise Exception("Fix the issue:(")
            continue
    return driver


def get_page_urls(class_name, timeout):
    driver1 = get_driver(LOCATION_URL, class_name, timeout)
    logger.info(f"pulling the data from {LOCATION_URL}")
    sel1 = html.fromstring(driver1.page_source)
    uls = sel1.xpath('//*[contains(@ng-if, "stores.length")]/li')
    ln_sn_page_urls = []
    for ul in uls:
        ln = ul.xpath('.//span[@class="name"]/text()')
        ln = " ".join("".join(ln).split())
        ln_pu = ln.lower().replace(" ", "-")
        sn = ul.xpath('.//span[@class="number"]/span/text()')[0]
        sn = "".join(sn.split()).replace("#", "")
        sn_pu = sn

        grid_id = ul.xpath('.//span[contains(@id, "store-preview")]/@id')[0]
        grid_id_pu = grid_id.replace("store-preview-", "").replace("--name", "")
        pu = f"https://www.weismarkets.com/stores/{ln_pu}-{sn_pu}/{grid_id_pu}"
        ln_sn_page_urls.append((ln, sn, pu))
    return ln_sn_page_urls


def fetch_records(idx, ln_sn_purl, sgw: SgWriter):
    MISSING = SgRecord.MISSING
    location_name, store_number, page_url = ln_sn_purl
    class_name2 = "hours-and-contact-header"
    timeout1 = 40
    driver2 = get_driver(page_url, class_name2, timeout1)
    sel2 = html.fromstring(driver2.page_source)

    street_address = sel2.xpath('//meta[@property="og:street-address"]/@content')
    street_address = "".join(street_address)
    street_address = street_address if street_address else MISSING

    city = sel2.xpath('//meta[@property="og:locality"]/@content')
    city = "".join(city)
    city = city if city else MISSING
    logger.info(f"[{idx}] City: {city}")

    state = sel2.xpath('//meta[@property="og:region"]/@content')
    state = "".join(state)
    state = state if state else MISSING

    zip_postal = sel2.xpath('//meta[@property="og:postal-code"]/@content')
    zip_postal = "".join(zip_postal)
    zip_postal = zip_postal if zip_postal else MISSING

    country_code = sel2.xpath('//meta[@property="og:country-name"]/@content')
    cc = "".join(country_code)
    country_code = cc if cc else MISSING

    latitude = sel2.xpath('//meta[@property="og:location:latitude"]/@content')
    latitude = "".join(latitude)
    latitude = latitude if latitude else MISSING

    longitude = sel2.xpath('//meta[@property="og:location:longitude"]/@content')
    longitude = "".join(longitude)
    longitude = longitude if longitude else MISSING

    location_type = MISSING
    try:
        phone = sel2.xpath('//meta[@property="og:phone_number"]/@content')
        phone = "".join(phone)
    except:
        phone = MISSING

    hours = ""
    days = sel2.xpath('//dl[contains(@aria-label, "Store Hours")]/dt/text()')
    hours_list = sel2.xpath('//dl[contains(@aria-label, "Store Hours")]/dd//text()')

    for x in range(len(days)):
        day = days[x].strip()
        hour = hours_list[x].strip()
        hours = hours + day + " " + hour + "; "
    hours = hours.rstrip(";")
    raw_address = MISSING

    item = SgRecord(
        locator_domain="weismarkets.com",
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours,
        raw_address=raw_address,
    )
    sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    class_name1 = "store-preview__info"
    logger.info(f"Class Name: {class_name1}")
    timeout = 60
    page_urls = get_page_urls(class_name1, timeout)
    logger.info(f"page urls: {page_urls[0:2]}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, idx, store_url, sgw)
            for idx, store_url in enumerate(page_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
