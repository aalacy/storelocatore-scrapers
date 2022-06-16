import re
import time
from lxml import html
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET

from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton

website = "https://www.dominos.co.in"
sitemap_url = f"{website}/store-locations/sitemap_area.xml"
MISSING = SgRecord.MISSING
max_workers = 12

headers = {
    "authority": "www.dominos.co.in",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": 'marketingChannel=https://www.dominos.co.in/store-locations/new-delhi/tis-hazari-metro-station-new-delhi / Direct; brandreferral=yes; brandreferral=yes; marketingChannel=https://www.dominos.co.in/store-locations/pizza-delivery-food-restaurants-in-ip-extention-shivani-appt-new-delhi-110092-area / Direct; _gcl_au=1.1.1765957974.1653051074; _ga=GA1.3.1517776804.1653051074; _fbp=fb.2.1653051075823.218470908; _gid=GA1.3.270757678.1654606888; _clck=3uzzqe|1|f24|0; hidden=value; PHPSESSID=lkqpdhkkn5hb3tj9gdsau1pjl9; marketingChannel=https://www.dominos.co.in/ / Direct; brandreferral=yes; __sts={"sid":1654608686731,"tx":1654608686731,"url":"https%3A%2F%2Fwww.dominos.co.in%2F","pet":1654608686731,"set":1654608686731}; __stp={"visit":"new","uuid":"65fc630e-4661-4d12-bb9c-507c069b4513"}; __stdf=0; __stgeo="0"; __stbpnenable=0; _uetsid=f1f295a0e66111ecba7bc17941e78770; _uetvid=2fc3e7a0971711ecbf8f913b4c7ef76e; WZRK_S_44Z-RW9-694Z=%7B%22p%22%3A9%7D; _dc_gtm_UA-45014247-1=1; _dc_gtm_UA-45014247-9=1; XSRF-TOKEN=eyJpdiI6ImRBTG5FTTZsK0JCaEpnRjBDOVFWT2c9PSIsInZhbHVlIjoiV29nRWl3YlUrTUZDNVlvOXJQRmRUUG5XeDkrWXBJRzMxQjNzaUpNOVQ1Qkp4VTc0aitmTUN3dkdHS0o4QURYVCIsIm1hYyI6IjVhNTU5MThhMGM1MmMzYjYwN2FmZmQ1YWUwYzA0MTFkOGM5ZTZiZGJlYTM1Y2M3YjU2ZmMxZDkyMTU3YzFiYjUifQ%3D%3D; jubilant_session=eyJpdiI6ImlWdUxTR3c0WWNjMkgxMTZcL1NQczh3PT0iLCJ2YWx1ZSI6IklOenk0eUx5ZmtmSUducnIwcHo3RUt1YjhUcGlDS0s2clo5aUNRNFBpNXllQit3dmZBNWNtaTBoY3VTY2N1NlYiLCJtYWMiOiJjMDQ4NjJkZWUwN2E2NTg2Y2ZhNDhiZTJkY2I4Y2FjYTZjNmQ3ZWI4NzEzODIwZDg1MGRlMGU2MWU0MGRkZGUzIn0%3D; _clsk=9x8ilv|1654610141421|5|1|l.clarity.ms/collect',
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}

session = SgRequests(proxy_country="in")
log = sglog.SgLogSetup().get_logger(logger_name=website)


def is_numeric(string):
    if string is None:
        return False
    string = f"{string}".strip()
    return string.isnumeric()


def request_with_retries(url, retry=1):
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 404:
            return -1, url
        if response.status_code != 200:
            return request_with_retries(url, retry + 1)
        return response.text, url
    except Exception as e:
        log.info(f"Failed {url}: err: {e}")
        pass
    if retry > 4:
        return None, url
    return request_with_retries(url, retry + 1)


def request_with_retries_stores(url, retry=1):
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 404:
            return -1, url
        if response.status_code != 200:
            return request_with_retries_stores(url, retry + 1)
        l1, l2 = get_lat_lng(response.text)
        if l1 == MISSING or l2 == MISSING and retry > 5:
            return request_with_retries_stores(url, retry + 1)
        return response.text, url

    except Exception as e:
        if retry > 4:
            log.info(f"Failed {url}:: Retried: {retry} err: {e}")
            return None, url
        return request_with_retries_stores(url, retry + 1)


def fetch_stores():
    response, url = request_with_retries(sitemap_url)
    if response is None:
        return []
    root = ET.fromstring(response)
    locations = []
    for elem in root:
        for var in elem:
            if "loc" in var.tag:
                locations.append(var.text)

    log.info(f"Total locations = {len(locations)}")

    page_urls = []
    count = 0
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for response, url in executor.map(request_with_retries, locations):
            count = count + 1
            if response is None or response == "":
                continue
            try:
                body = html.fromstring(response, "lxml")
                urls = body.xpath("//h3/a/@href")
                for url in urls:
                    if url not in page_urls:
                        page_urls.append(url)
            except Exception as e:
                log.info(f"Error Fetching Store: {e}")
                pass
            if count % 50 == 0:
                log.debug(f"{count} page_urls {len(page_urls)}")

    log.info(f"Total page_urls {len(page_urls)}")
    return page_urls


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
        log.info(f"Address Missing:{raw_address}, Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def split_text(text, variable):
    try:
        val = text.split(variable + '":')[1].splitlines()[0].replace(",", "")
        return val
    except Exception as e:
        log.info(f"Text Splitting Err: {e}")
        return MISSING


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def get_ra(address):
    if len(address) == 0:
        return MISSING
    address = address[0]
    address = address.split(", PH.NO.")[0].strip()
    address = address.split("PH.NO.")[0].strip()
    if "phone" in address.lower():
        address = address.lower().split("phone")[0].strip().capitalize()
    if "ph." in address.lower():
        address = address.lower().split("ph.")[0].strip().capitalize()
    if "ph-" in address.lower():
        address = address.lower().split("ph-")[0].strip().capitalize()
    if "ph " in address.lower():
        address = address.lower().split("ph ")[0].strip().capitalize()

    address = " ".join(address.rsplit("-", 1))
    phone = get_phone(address)
    address = address.replace(phone, "  ").strip()
    address = address.replace(",,", ",").replace(",", ", ").strip()
    return " ".join(address.split())


def get_lat_lng(response):
    lat = split_text(response, "latitude")
    lng = split_text(response, "longitude")
    if lat != MISSING and lng != MISSING:
        return lat, lng

    try:
        parts = response.split("LatLng(")[1].split(");")[0].split(",")
        if len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
            return parts[0].strip(), parts[1].strip()
    except Exception as e:
        log.info(f"Lat/Lng Err: {e}")
        pass
    return lat, lng


def fetch_data():
    page_urls = fetch_stores()
    log.info(f"Total stores = {len(page_urls)}")
    count = 0

    location_type = MISSING
    store_number = MISSING
    country_code = "IN"

    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for response, page_url in executor.map(request_with_retries_stores, page_urls):
            count = count + 1
            try:
                if response is None:
                    continue

                if response == -1:
                    continue
                log.info(f"{count}. fetching {page_url} ...")
                body = html.fromstring(response, "lxml")

                location_name = body.xpath("//h1/text()")[0].strip()
                raw_address = get_ra(
                    body.xpath('//h2[contains(@class, "store-page-address")]/text()')
                )
                street_address, city, state, zip_postal = get_address(raw_address)
                latitude, longitude = get_lat_lng(response)
                phone = body.xpath('//a[contains(@href, "tel:")]/p/text()')
                if len(phone) > 0:
                    phone = phone[0]
                else:
                    phone = MISSING

                hours_of_operation = body.xpath(
                    '//p[contains(@class, "fontsize4 bold")]/text()'
                )
                if len(hours_of_operation) > 0:
                    hours_of_operation = hours_of_operation[0]
                    hours_of_operation = (
                        hours_of_operation.replace("\\n", " ")
                        .replace("\\N", " ")
                        .strip()
                    )
                    if hours_of_operation.lower() in ["to", "closed to closed"]:
                        hours_of_operation = MISSING
                    if hours_of_operation.lower().startswith("to "):
                        hours_of_operation = MISSING
                else:
                    hours_of_operation = MISSING
                if location_name == MISSING or raw_address == MISSING:
                    continue

                if is_numeric(state):
                    state = MISSING
                    if zip_postal == MISSING:
                        zip_postal = f"{state}"

                if is_numeric(city):
                    city = MISSING
                    if zip_postal == MISSING:
                        zip_postal = f"{city}"

                if city.lower() in ["pin", "code", "pin code"]:
                    city = MISSING
                if " pin code" in city.lower():
                    parts = city.lower().split("pin code")
                    city = parts[0]
                    if len(parts) > 1 and is_numeric(parts[1].strip()):
                        zip_postal = parts[1].strip()
                if " pin" in city.lower():
                    city = (
                        city.replace(" pin", "")
                        .replace(" Pin", "")
                        .replace(" PIN", "")
                        .strip()
                    )

                yield SgRecord(
                    locator_domain=website,
                    store_number=store_number,
                    page_url=page_url,
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
            except Exception as e:
                log.info(f"Failed Adding Data, Err: {e}")
                pass
    return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    CrawlStateSingleton.get_instance().save(override=True)
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
