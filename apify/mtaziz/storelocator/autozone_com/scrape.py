from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgselenium import SgChrome
from tenacity import retry, stop_after_attempt
import tenacity
import re
from lxml import html
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


MAX_WORKERS = 5
logger = SgLogSetup().get_logger(logger_name="autozone_com")
locator_domain_url = " https://www.autozone.com"


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_all_raw_store_urls():

    url_sitemap_main = "https://www.autozone.com/locations/sitemap.xml"
    with SgChrome() as driver:
        driver.get(url_sitemap_main)
        time.sleep(30)
        pgsrc = driver.page_source
        datar = html.fromstring(bytes(pgsrc, encoding="utf8"))
        raw_store_urls = datar.xpath("//url/loc/text()")
        return raw_store_urls


def get_filtered_urls():
    all_raw_store_urls = get_all_raw_store_urls()
    logger.info("Removing irrelevant urls")
    pattern_tx1 = r"\/[batteries, brakes]\w+.html"
    pattern_tx2 = r"((?=.*\d).+)"
    url_tx_reg1 = []
    url_tx_reg2 = []
    for i in all_raw_store_urls:
        reg_tx1 = re.findall(pattern_tx1, i)
        if not reg_tx1:
            url_tx_reg1.append(i)
    for j in url_tx_reg1:
        reg_tx2 = re.findall(pattern_tx2, j)
        if reg_tx2:
            url_tx_reg2.append(j)
    url_tx_reg2 = [
        url for url in url_tx_reg2 if "/es/" not in url
    ]  # Remove spanish language based urls
    return url_tx_reg2


def get_hoo(hoo_details):
    hoo = []
    for td in hoo_details:
        week_date = td.xpath("./td/text()")
        week_date = "".join(week_date)
        logger.info(f"Week Day: {week_date}")
        date_time = td.xpath("./td/span/span/text()")
        date_time = " ".join(date_time)
        logger.info(f"Week Day Time: {date_time}")
        hoo_per_day = f"{week_date} {date_time}"
        hoo.append(hoo_per_day)
    hoo = "; ".join(hoo)
    logger.info(f"Hours of Operation: {hoo}")

    if hoo:
        return hoo
    else:
        return SgRecord.MISSING


def fetch_records(idx, url, sgw: SgWriter, driver):
    driver.get(url)

    data_raw = html.fromstring(driver.page_source, "lxml")
    logger.info(f"[{idx}] PullingDataFrom: {url}")
    locator_domain = locator_domain_url
    page_url = url if url else SgRecord.MISSING

    location_name = data_raw.xpath('//h1[@class="c-location-title"]/span/text()')
    location_name = " ".join(location_name)
    logger.info(f"Location Name: {location_name}")

    street_address = data_raw.xpath('//meta[@itemprop="streetAddress"]/@content')
    street_address = "".join(street_address).strip()
    street_address = street_address if street_address else SgRecord.MISSING
    logger.info(f"street_address: {street_address}")

    city = data_raw.xpath('//span[@itemprop="addressLocality"]/text()')
    city = "".join(city).strip()
    city = city if city else SgRecord.MISSING
    logger.info(f"City Name: {city}")

    state = data_raw.xpath('//abbr[@itemprop="addressRegion"]/text()')
    state = "".join(state).strip()
    state = state if state else SgRecord.MISSING
    logger.info(f"State Name: {state}")

    zipcode = data_raw.xpath('//span[@itemprop="postalCode"]/text()')
    zipcode = "".join(zipcode).strip()
    zip = zipcode if zipcode else SgRecord.MISSING
    logger.info(f"Zip: {zip}")

    country_code = "US"
    try:
        store_number = location_name.split("#")[1]
    except:
        store_number = SgRecord.MISSING
    logger.info(f"Store Number: {store_number}")

    phone = data_raw.xpath('//span[@itemprop="telephone"]/text()')
    phone = "".join(phone).strip()
    phone = phone if phone else SgRecord.MISSING
    logger.info(f"Phone Number: {phone}")

    location_type_xpath = '//a[contains(@data-ya-track, "servicesavail")]/text()'
    location_type = data_raw.xpath(location_type_xpath)
    location_type = ", ".join(location_type).strip()
    location_type = location_type if location_type else SgRecord.MISSING
    logger.info(f"Location Type: {location_type}")

    latitude_xpath = '//meta[@itemprop="latitude"]/@content'
    latitude = data_raw.xpath(latitude_xpath)
    latitude = "".join(latitude).strip()
    latitude = latitude if latitude else SgRecord.MISSING
    logger.info(f"Latitude: {latitude}")

    longitude_xpath = '//meta[@itemprop="longitude"]/@content'
    longitude = data_raw.xpath(longitude_xpath)
    longitude = "".join(longitude).strip()
    longitude = longitude if longitude else SgRecord.MISSING
    logger.info(f"Longitude: {longitude}")

    hoo_details_xpath = '//table[@class="c-location-hours-details"]/tbody/tr'
    hoo_details = data_raw.xpath(hoo_details_xpath)
    hours_of_operation = get_hoo(hoo_details)
    raw_address = SgRecord.MISSING

    item = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zipcode,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )
    sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    all_store_urls = get_filtered_urls()
    logger.info(f"Store URLs count: {len(all_store_urls)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        with SgChrome() as driver:
            task = [
                executor.submit(fetch_records, idx, url, sgw, driver)
                for idx, url in enumerate(all_store_urls[0:])
            ]
            for future in as_completed(task):
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
