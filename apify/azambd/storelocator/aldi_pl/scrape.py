from lxml import html
import time
from xml.etree import ElementTree as ET
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.aldi.pl"
sitemap_url = f"{website}/.aldi-nord-sitemap-pages.xml"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetch_stores():
    response = request_with_retries(sitemap_url)
    page_urls = []
    root = ET.fromstring(response.text)
    for elem in root:
        for var in elem:
            if "loc" in var.tag and "wyszukiwarka-sklepu" in var.text:
                page_urls.append(var.text)
    return page_urls


def fetch_store(page_url):
    try:
        response = request_with_retries(page_url)
        if '"pageType":"Store details"' in response.text:
            return html.fromstring(response.text, "lxml")
    except Exception as e:
        log.info(f"Failed page: {page_url} and Err: {e}")
        pass
    return None


def stringify_nodes(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def fetch_data():
    page_urls = fetch_stores()
    log.info(f"Total page_urls = {len(page_urls)}")
    count = 0
    page_count = 0

    store_number = MISSING
    location_type = MISSING
    state = MISSING
    phone = MISSING
    latitude = MISSING
    longitude = MISSING
    country_code = "PL"

    for page_url in page_urls:
        count = count + 1
        body = fetch_store(page_url)
        if body is None:
            continue
        page_count = page_count + 1
        log.debug(f"{count} - {page_count} . scrapping {page_url} ...")

        location_name = stringify_nodes(
            body, '//div[contains(@class, "mod mod-headline")]/h2'
        )
        street_address = stringify_nodes(
            body, '//span[contains(@itemprop, "streetAddress")]'
        )
        city = stringify_nodes(body, '//span[contains(@itemprop, "addressLocality")]')
        zip_postal = stringify_nodes(body, '//span[contains(@itemprop, "postalCode")]')
        hours_of_operation = (
            stringify_nodes(
                body, '//div[contains(@class, "mod-stores__detail-col")][2]'
            )
            .replace("Godziny otwarcia", "")
            .replace(".-", "-")
            .strip()
        )
        raw_address = f"{street_address}, {city} {zip_postal}".replace(MISSING, "")
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        yield SgRecord(
            locator_domain="aldi.pl",
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
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
