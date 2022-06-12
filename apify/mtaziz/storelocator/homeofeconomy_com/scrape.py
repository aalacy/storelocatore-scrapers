from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from lxml import html
import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import json
import ssl
import pyppdf.patch_pyppeteer
import logging

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


LOCATION_URL = "https://homeofeconomy.net/"
DOMAIN = "homeofeconomy.net"
logger = SgLogSetup().get_logger(logger_name="homeofeconomy_net")
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}

# To fix - certificate verify failed: unable to get local issuer, we have used this library pyppdf
logger.info(f"pyppdf loaded: {pyppdf.patch_pyppeteer}")

pyppeteer_level = logging.WARNING
logging.getLogger("pyppeteer").setLevel(pyppeteer_level)
logging.getLogger("websockets.protocol").setLevel(pyppeteer_level)


def get_store_urls(http: SgRequests):
    res = http.get(LOCATION_URL, headers=headers)
    sel_stores = html.fromstring(res.text)
    store_urls = sel_stores.xpath('//li/a[contains(@href, "stihldealer")]/@href')
    return store_urls


def fetch_record(content, store_url):
    page_sel = html.fromstring(content, "lxml")
    page_url = store_url
    locator_domain = DOMAIN
    json_text = "".join(page_sel.xpath('//script[@type="application/ld+json"]/text()'))

    json_body = json.loads(json_text)
    location_name = json_body["name"].strip()
    street_address = json_body["address"]["streetAddress"].strip()

    city = json_body["address"]["addressLocality"].strip()
    state = json_body["address"]["addressRegion"].strip()
    zip_postal = json_body["address"]["postalCode"].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = json_body["telephone"].strip()
    location_type = "<MISSING>"
    days = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    hours_info = []
    for day, index in days.items():
        if "opens" in json_body["openingHoursSpecification"][index]:
            opens = json_body["openingHoursSpecification"][index]["opens"]
            closes = json_body["openingHoursSpecification"][index]["closes"]
            hours_info.append(f"{day}: {opens} - {closes}")
        else:
            hours_info.append(f"{day}: Closed")
    hours_of_operation = "; ".join(hours_info)

    latitude = json_body["geo"]["latitude"].strip()
    longitude = json_body["geo"]["longitude"].strip()
    raw_address = "<MISSING>"
    return SgRecord(
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


async def get_response(url):
    driver = await launch(headless=True, args=["--no-sandbox"])
    page = await driver.newPage()
    await stealth(page)
    await page.goto(url)
    time.sleep(5)
    html_content = await page.content()
    await driver.close()
    data = fetch_record(html_content, url)
    return data


def main_generator():
    with SgRequests() as http:
        urls = get_store_urls(http)
        loop = asyncio.get_event_loop()
        for idx, url in enumerate(urls[0:]):
            for future in asyncio.as_completed([get_response(url)]):
                yield loop.run_until_complete(future)


def scrape():
    for rec in main_generator():
        count = 0

        with SgWriter(
            SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))
        ) as writer:
            writer.write_row(rec)
            count = count + 1
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
