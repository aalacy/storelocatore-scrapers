import time
import re
from lxml import html
import ssl
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "westbrom.co.uk"
website = "https://www.westbrom.co.uk"
branch_page = f"{website}/customer-support/branch-finder"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    response = session.get(url, headers=headers)
    return html.fromstring(response.text, "lxml")


def fetch_stores():
    page_urls = []
    body = request_with_retries(
        "https://www.bankopeningtimes.co.uk/west-bromwich-building-society/west-bromwich-building-society.html"
    )

    for a in body.xpath("//li/a"):
        if "West Bromwich Building Society In" in a.xpath(".//text()")[0]:
            loc = a.xpath(".//@href")[0].replace(".html", "")
            page_urls.append(
                "http://www.westbrom.co.uk/customer-support/branch-finder/" + loc
            )
    return page_urls


def stringify_nodes(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.replace("&nbsp;", " ")
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_lat_lng(nodes=[]):
    if len(nodes) == 0:
        return MISSING, MISSING

    href = nodes[0]
    href = href.replace("https://www.google.co.uk/maps/place/", "")
    if "," not in href:
        return MISSING, MISSING
    parts = href.split(",")
    return parts[0], parts[1]


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def get_address(raw_address):
    try:
        parts = raw_address.split(",")
        count = len(parts)
        sa = parts[0].strip()
        for index in range(1, count - 2):
            sa = sa + ", " + parts[index].strip()
        return sa, parts[count - 2].strip(), MISSING, parts[count - 1].strip()
    except Exception as e:
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    page_urls = fetch_stores()
    log.info(f"Total stores = {len(page_urls)}")
    store_number = MISSING
    location_type = MISSING
    country_code = "UK"
    count = 0
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. scrapping {page_url} ...")
        body = request_with_retries(page_url)
        try:
            location_name = body.xpath("//h1/text()")[0]
        except Exception as e:
            log.info(f"Location Name Error: {e}")
            continue
        raw_address = (
            stringify_nodes(body, '//div[@class="branch-details__location"]')
            .replace("Location", "")
            .strip()
        )
        street_address, city, state, zip_postal = get_address(raw_address)
        phone = get_phone(
            stringify_nodes(body, '//div[@class="branch-details__contact"]')
        )
        latitude, longitude = get_lat_lng(
            body.xpath('//a[contains(@href, "https://www.google.co.uk/maps")]/@href')
        )
        hours_of_operation = (
            stringify_nodes(body, '//table[@class="branch-details__opening-times"]')
            .replace(" (tomorrow)", "")
            .replace(" (today)", "")
        )

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
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
