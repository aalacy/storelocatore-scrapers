from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ssl
from lxml import html
import time

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


LOCATION_URL = "https://www.weismarkets.com/stores/?coordinates=40.539711620149,-75.733030850299&zoom=10"
MAX_WORKERS = 1
DOMAIN = "weismarkets.com/pharmacy"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("weismarkets_com__pharmacy")  # noqa

headers = {
    "accept": "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "MMozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
)


def get_page_urls():
    base_url = "https://www.weismarkets.com/"
    class_name_main_nav = "main-navigation"
    timeout3 = 40
    with SgChrome(driver_wait_timeout=180) as driver:
        driver.get(base_url)
        WebDriverWait(driver, timeout3).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name_main_nav))
        )
        stores_link_xpath = '//*[contains(@data-original-title, "Stores") and contains(@href, "stores#")]'
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, stores_link_xpath))
        )
        driver.find_element_by_xpath(stores_link_xpath).click()
        time.sleep(20)
        logger.info("Store Clicked!")
        logger.info("Pulling the data for store URL")
        sel1 = html.fromstring(driver.page_source)
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


def fetch_data():
    logger.info("Pulling store URLs")
    page_urls = None
    store_urls = get_page_urls()
    if not store_urls:
        page_urls = get_page_urls()
    else:
        page_urls = store_urls

    logger.info(f"Store URLs Scraping Finished: {page_urls[0:5]}")  # noqa
    with SgChrome(block_third_parties=True, driver_wait_timeout=180) as driver:
        for idx, ln_sn_purl in enumerate(page_urls[0:]):
            location_name, store_number, page_url = ln_sn_purl
            driver.get(page_url)
            driver.implicitly_wait(5)
            logger.info(f"[{idx}] Pulling the data for {page_url}")  # noqa
            sel2 = html.fromstring(driver.page_source)

            street_address = sel2.xpath(
                '//meta[@property="og:street-address"]/@content'
            )
            street_address = "".join(street_address)
            street_address = street_address if street_address else MISSING

            city = sel2.xpath('//meta[@property="og:locality"]/@content')
            city = "".join(city)
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")  # noqa

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

            location_type = "General Store"
            try:
                phone = sel2.xpath('//meta[@property="og:phone_number"]/@content')
                phone = "".join(phone)
            except:
                phone = MISSING

            hours = []
            hoo = ""
            try:
                days = sel2.xpath(
                    '//dl[contains(@aria-label, "Store Hours")]/dt/text()'
                )
                hours_list = sel2.xpath(
                    '//dl[contains(@aria-label, "Store Hours")]/dd//text()'
                )

                for x in range(len(days)):
                    day = days[x].strip()
                    hour = hours_list[x].strip()
                    day_hour = day + " " + hour
                    hours.append(day_hour)
                hoo = "; ".join(hours)

            except:
                hoo = MISSING

            # Pharmacy Conditions
            xpath_pharmacy = '//h2[contains(text(), "Pharmacy")]'
            pharmacy_exist = sel2.xpath(xpath_pharmacy)
            if pharmacy_exist:
                logger.info(f"<< Pharmacy Exists at {page_url} >>")

                # Pharmacy Phone
                xpath_phone_pharmacy = (
                    '//a[span[contains(text(), "Pharmacy Phone number:")]]/text()'
                )
                phone_pharmacy = sel2.xpath(xpath_phone_pharmacy)
                phone_pharmacy_cl = ["".join(i.split()) for i in phone_pharmacy]
                if phone_pharmacy_cl:
                    phone = "".join(phone_pharmacy_cl)
                else:
                    phone = MISSING

                # Pharmacy Location Type
                location_type = "Pharmacy"

                # Pharmacy Hours
                try:
                    hours_pharmacy = []
                    days_pharmacy = sel2.xpath(
                        '//dl[contains(@class, "store-details-department-hours")]/dt/text()'
                    )
                    hours_list_ph = sel2.xpath(
                        '//dl[contains(@class, "store-details-department-hours")]/dd//text()'
                    )
                    logger.info(
                        f"<< Raw Days Data Pharmacy:  {days_pharmacy} >> "
                    )  # noqa
                    logger.info(f"<< Hours Data Pharmacy:  {hours_list_ph} >> ")  # noqa

                    for x in range(len(days_pharmacy)):
                        day_ph = days_pharmacy[x].strip()
                        hour_ph = hours_list_ph[x].strip()
                        day_hour_ph = day_ph + " " + hour_ph
                        hours_pharmacy.append(day_hour_ph)
                    hoo = "; ".join(hours_pharmacy)
                    logger.info(f"Pharmacy Hours")  # noqa
                except Exception as e:
                    hoo = MISSING
                    logger.info(
                        f"Fix Pharmacy Hours: << {e} >> at {days_pharmacy} | {hours_list_ph}"
                    )  # noqa

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
                hours_of_operation=hoo,
                raw_address=raw_address,
            )
            yield item


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
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
