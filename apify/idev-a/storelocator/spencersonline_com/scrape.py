import math
import re
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET
import time

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

DOMAIN = "spencersonline.com"
website = "https://www.spencersonline.com"
MISSING = "<MISSING>"


headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


max_workers = 2


def fetchConcurrentSingle(data):
    response = request_with_retries(data["url"])
    return data["url"], response.text.replace(" ='", " = '").replace('"', "'").replace(
        "='", " = '"
    )


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            count = count + 1
            if count % reminder == 0:
                log.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetchStores():
    response = request_with_retries(f"{website}/sitemap/SPN_store_1.xml")
    data = ET.fromstring(response.text)
    urls = []
    for element in data:
        for el in element:
            if el.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}loc":
                urls.append({"url": el.text})
    return urls


def getJSObject(response, varName):
    JSObject = re.findall(f"{varName} = '(.+?);", response)
    if JSObject is None or len(JSObject) == 0:
        return MISSING
    return cleanString(JSObject[0])


def cleanString(value):
    value = (
        value.replace("'", "")
        .replace("&#45;", "-")
        .replace("&#39;", "'")
        .replace("&#45", "-")
        .replace("&#39", "'")
    )
    if value is None or len(value) == 0 or value == "0":
        return MISSING
    return value


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    for page_url, response in fetchConcurrentList(stores):
        store_number = getJSObject(response, "store.STORE_NUMBER")
        location_name = getJSObject(response, "store.STORE_NAME")
        al1 = getJSObject(response, "store.ADDRESS_LINE_1")
        al2 = getJSObject(response, "store.ADDRESS_LINE_2")
        city = getJSObject(response, "store.CITY")
        state = getJSObject(response, "store.STATE")
        status = getJSObject(response, "store.STORE_STATUS")
        country_code = getJSObject(response, "store.COUNTRY_CODE")
        phone = getJSObject(response, "store.PHONE")
        latitude = getJSObject(response, "store.LATITUDE")
        longitude = getJSObject(response, "store.LONGITUDE")
        zip_postal = getJSObject(response, "store.ZIP_CODE")

        location_type = MISSING
        street_address = al2.strip() or MISSING
        if street_address == MISSING:
            street_address = al1.strip()

        hours_of_operation = MISSING
        if "CL" in status:
            hours_of_operation = "Closed"
        raw_address = f"{street_address}, {city}, {state} {zip_postal}"

        if "X, X," in raw_address:
            street_address = MISSING
            city = MISSING
            raw_address = MISSING

        yield SgRecord(
            locator_domain=DOMAIN,
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
    return []


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"{end-start} seconds.")


session.close()
if __name__ == "__main__":
    scrape()
