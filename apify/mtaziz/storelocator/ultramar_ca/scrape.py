from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sglogging import SgLogSetup
from lxml import html
from time import sleep
from random import randint
from sgselenium import SgChrome, SgSelenium
from webdriver_manager.chrome import ChromeDriverManager

logger = SgLogSetup().get_logger(logger_name="ultramar_ca")
MISSING = SgRecord.MISSING
locator_domain_url = "https://www.ultramar.ca"
MAX_WORKERS = 6


STORE_LOCATOR = "https://www.ultramar.ca/en-on/find-services-stations/"


def get_headers_for(url: str) -> dict:
    with SgChrome(executable_path=ChromeDriverManager().install()) as chrome:
        headers = SgSelenium.get_default_headers_for(chrome, url)
    return headers  # type: ignore


def get_station_location_type(data_r_location_type, url):
    loctype_dict = {}
    loctype_list = []
    xpath_emart = '//div[h2[contains(text(), "Products and services")]]/ul[@class="station__icons-list"]/li//text()'
    data_icon_list = data_r_location_type.xpath(xpath_emart)
    data_icon_list = [" ".join(i.split()) for i in data_icon_list]
    data_icon_list = [i.replace("Open 24h", "") for i in data_icon_list]
    data_icon_list = [i for i in data_icon_list if i]
    data_icon_list = "; ".join(data_icon_list)
    loctype_dict = {"page_url": url, "location_type": data_icon_list}
    loctype_list.append(loctype_dict)
    return loctype_dict


def get_human_hours(data_store):
    xpath_hoo1 = '//div[img[@alt="24h clock"]]/text()'
    hoo1_raw = data_store.xpath(xpath_hoo1)
    hoo1 = [" ".join(i.split()) for i in hoo1_raw]
    hoo1 = [i for i in hoo1 if i]
    weekdays = data_store.xpath(
        '//div[img[@alt="24h clock"]]/meta[@itemprop="openingHours"]/@content'
    )
    weekdays = "".join(weekdays)
    logger.info(f"weekdays: {weekdays}")
    hoo1 = "".join(hoo1)
    logger.info(f"HOO1 : {hoo1}")
    hoo = ""
    try:
        if not hoo1:
            idx = "1"
            logger.info(f"Hours of Operation Raw Data1: {hoo}")
            xpath_hoo2 = '//div[img[@alt="24h clock"]]/div[@class="station__hours"]/div'
            hoo2_list = []
            hoo2_obj = data_store.xpath(xpath_hoo2)
            logger.info(f"[{idx}] Hours of Operation Data2: {hoo2_obj}")
            for span in hoo2_obj:
                daytime = span.xpath(".//span/text()")
                daytime = " ".join(daytime)
                hoo2_list.append(daytime)
            hoo = "; ".join(hoo2_list)
        else:
            hoo = weekdays + ": " + hoo1
        logger.info(f"HOO: {hoo}")
    except:
        logger.info(f"Please check if HOO is empty: {data_store}")
        hoo = ""
    return hoo


def get_store_urls(headers, sitemap_url):
    with SgRequests() as http:
        logger.info("Pulling Store URLs from sitemap URL")
        r = http.get(sitemap_url, headers=headers)
        sel = html.fromstring(bytes(r.text, encoding="utf8"))
        station_urls = sel.xpath("//loc/text()")
        station_urls = [
            i
            for i in station_urls
            if "https://www.ultramar.ca/en/find-services-stations/" in i
        ]
        logger.info(f"Station Count: {len(station_urls)}")
        return station_urls


def fetch_records(idx, store_url, headers, sgw: SgWriter):

    with SgRequests() as http:

        r_store = http.get(store_url, headers=headers)
        sleep(randint(1, 4))
        data_store = html.fromstring(r_store.text, "lxml")
        locator_domain = locator_domain_url
        page_url = store_url.strip()
        logger.info(f"[{idx}] Scraping Data From: {page_url}\n")
        xpath_location_name = (
            '//*[contains(@class, "heading") and contains(@itemprop, "name")]/text()'
        )
        location_name = data_store.xpath(xpath_location_name)
        location_name = "".join(location_name).strip().replace("0000", "")
        location_name = location_name if location_name else MISSING
        logger.info(f"[{idx}] Location Name: {location_name}\n")

        xpath_address_data = (
            '//address/span[@class="station__coordinates-line"]//text()'
        )
        address_data = data_store.xpath(xpath_address_data)
        address_data = [" ".join(i.split()) for i in address_data]
        address_data = [i.strip(",") for i in address_data if i]
        address_data = [i for i in address_data if i]
        logger.info(f"[{idx}] address data: {address_data}")

        street_address = address_data[0] if address_data[0] else MISSING

        city = address_data[1] or MISSING
        state = address_data[2] or MISSING
        zip_postal = address_data[-1] or MISSING
        country_code = "CA"
        store_number = MISSING

        xpath_phone = '//span[contains(@itemprop, "telephone")]/text()'
        phone_data = data_store.xpath(xpath_phone)[0].strip()
        phone = phone_data if phone_data else MISSING

        location_type_data = get_station_location_type(data_store, store_url)
        if location_type_data["location_type"]:
            location_type = location_type_data["location_type"]
        else:
            location_type = MISSING
        latitude = data_store.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = "".join(latitude)

        longitude = data_store.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = "".join(longitude)

        hours_of_operation = get_human_hours(data_store)

        raw_address = MISSING
        item = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
        sgw.write_row(item)


def fetch_data(headers, sgw: SgWriter):
    sitemap_stores_url = "https://www.ultramar.ca/sitemap-stores.xml"
    store_urls = get_store_urls(headers, sitemap_stores_url)
    logger.info(f"Total Countries to be crawled: {len(store_urls)}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, storenum, store_url, headers, sgw)
            for storenum, store_url in enumerate(store_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    headers = get_headers_for(STORE_LOCATOR)
    logger.info(f"headers: {headers}")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(headers, writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
