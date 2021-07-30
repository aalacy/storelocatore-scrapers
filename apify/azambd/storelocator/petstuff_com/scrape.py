from lxml import html
import time
import re

from sgscrape.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

website = "https://petstuff.com"
MISSING = "<MISSING>"
shop_url = "https://shop.petstuff.com"


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def getStringFromArrayElements(elements):
    value = ""
    for element in elements:
        element = (
            element.replace("\r", "")
            .replace("\n", "")
            .replace("&nbsp; ", "")
            .replace("&nbsp;", "")
            .replace("https://maps.google.com/?q= ", "")
            .strip()
        )
        element = re.sub(r"\s+", " ", element)
        if len(element):
            value = value + " " + element
    if len(value) == 0:
        return MISSING
    return value.strip()


def getJSObject(response, varName, noVal=MISSING):
    JSObject = re.findall(f'{varName} = "(.+?)";', response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            return street_address, data.city, data.state, data.postcode
    except Exception as e:
        log.info(f"Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetchStores(page=1, stores=[]):
    log.info(f"Scrapping stores from {shop_url}/stores/search/?page={page} ...")
    response = request_with_retries(f"{shop_url}/stores/search/?page={page}")
    body = html.fromstring(response.text, "lxml")
    nextPageDiv = body.xpath(
        '//a[contains(@class, "endless_page_link") and text() = "Next"]'
    )

    stores = stores + body.xpath('//a[@class="pull-right"]/@href')

    if len(nextPageDiv) > 0:
        return fetchStores(page + 1, stores)
    return stores


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    for urlPart in stores:
        page_url = f"{shop_url}{urlPart}".replace("/stores/view", "")
        response = request_with_retries(page_url)
        body = html.fromstring(response.text, "lxml")
        store_info = body.xpath('//div[@class="store-info-body"]')[0]
        location_name = getStringFromArrayElements(body.xpath("//h1/text()"))
        phone = getStringFromArrayElements(
            store_info.xpath('.//a[contains(@href, "tel")]/div/text()')
        )

        raw_address = getStringFromArrayElements(
            store_info.xpath('.//a[contains(@href, "maps.google")]/@href')
        )

        latitude = getJSObject(response.text, "latitude")
        longitude = getJSObject(response.text, "longitude")
        street_address, city, state, zip_postal = getAddress(raw_address)

        store_number = MISSING
        location_type = MISSING
        country_code = "US"

        hoo = []
        for hooDiv in store_info.xpath('.//div[@class="row stre-opn-tmngs"]'):
            hoo.append(getStringFromArrayElements(hooDiv.xpath(".//div/text()")))
        hours_of_operation = "; ".join(hoo)

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


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
