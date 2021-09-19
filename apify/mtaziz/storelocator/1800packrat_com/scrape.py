from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import json
import ssl
import pyppdf.patch_pyppeteer
from sgrequests import SgRequests

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger(logger_name="1800packrat_com")
# To fix - certificate verify failed: unable to get local issuer, we have used this library pyppdf
logger.info(f"pyppdf loaded: {pyppdf.patch_pyppeteer}")


LOCATION_URL = "https://www.1800packrat.com/locations"
DOMAIN = "1800packrat.com"
MISSING = SgRecord.MISSING
headers_custom_for_location_url = {
    "authority": "www.1800packrat.com",
    "method": "GET",
    "path": "/locations",
    "scheme": "https",
    "referer": "https://www.1800packrat.com/locations",
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "upgrade-insecure-requests": "1",
}
userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
args = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-infobars",
    "--window-position=0,0",
    "--ignore-certifcate-errors",
    "--ignore-certifcate-errors-spki-list",
    "--user-agent=" + userAgent,
]

options = {
    "args": args,
    "headless": True,
    "ignoreHTTPSErrors": True,
    "handleSIGINT": False,
    "handleSIGTERM": False,
    "handleSIGHUP": False,
}


def get_store_urls():
    with SgRequests() as http:
        geo = dict()
        urls = []
        r = http.get(
            LOCATION_URL,
            headers=headers_custom_for_location_url,
            timeout=180,
        )
        tree = html.fromstring(r.text)
        logger.info(f"Raw Page Source: {r.text}")
        text = (
            "".join(tree.xpath("//script[contains(text(), 'markers:')]/text()"))
            .split("markers:")[1]
            .split("]")[0]
            .strip()[:-1]
            + "]"
        )
        js = json.loads(text)
        for j in js:
            slug = j.get("Link")
            url = f"https://www.{DOMAIN}{slug}"
            urls.append(url)
            lat = j.get("Latitude") or MISSING
            lng = j.get("Longitude") or MISSING
            geo[slug] = {"lat": lat, "lng": lng}
            logger.info(f"Latitude & Longitude: {geo}")
        return urls, geo


def fetch_record(idx, content, store_url, latlng):
    logger.info(f"[{idx}] Pulling the data from {store_url}")
    page_sel = html.fromstring(content, "lxml")
    xpath_json_data = '//script[contains(@type, "application/ld+json") and contains(text(), "MovingCompany")]/text()'
    json_data = page_sel.xpath(xpath_json_data)
    json_data = "".join(json_data)
    json_data = " ".join(json_data.split())
    json_data = json.loads(json_data)
    page_url = json_data["url"]
    location_name = json_data["name"] or MISSING
    address = json_data["address"]
    sa = address["streetAddress"] or MISSING
    street_address = sa
    logger.info(f"[{idx}] Street Address: {street_address}")
    city = address["addressLocality"] or MISSING
    logger.info(f"[{idx}] city: {city}")

    state = address["addressRegion"] or MISSING
    logger.info(f"[{idx}] State: {state}")
    zip_postal = address["postalCode"] or MISSING
    logger.info(f"[{idx}] Zipcode: {zip_postal}")
    country_code = "US"
    store_number = MISSING
    phone = json_data["telephone"] or MISSING
    location_type = json_data["@type"]
    page_url_custom = page_url.replace("https://www.1800packrat.com", "").strip()
    lat = latlng[page_url_custom]["lat"] or MISSING
    latitude = lat
    logger.info(f"[{idx}] Latitude: {lat}")
    lng = latlng[page_url_custom]["lng"] or MISSING
    longitude = lng
    logger.info(f"[{idx}] Longitude: {lng}")
    locator_domain = "1800packrat.com"

    # Hours of Operation
    hoo = []
    for i in json_data["openingHoursSpecification"]:
        day_of_week = (
            i["dayOfWeek"].replace("http://schema.org/", "")
            + " "
            + str(i["opens"] or "")
            + " - "
            + str(i["closes"] or "")
        )
        hoo.append(day_of_week)
    hours_of_operation = "; ".join(hoo)
    logger.info(f"[{idx}] HOO: {hours_of_operation}")
    raw_address = MISSING
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


async def get_response(idx, url, latlng):
    driver = await launch(options)
    page = await driver.newPage()
    await stealth(page)
    await page.goto(url)
    await asyncio.sleep(5)
    html_content = await page.content()
    await driver.close()
    data = fetch_record(idx, html_content, url, latlng)
    return data


def main_generator():

    urls, geo = get_store_urls()
    logger.info(f"List of Store URLs: {urls}")
    loop = asyncio.get_event_loop()
    for idx, url in enumerate(urls[0:]):
        for future in asyncio.as_completed([get_response(idx, url, geo)]):
            yield loop.run_until_complete(future)


def scrape():
    for rec in main_generator():
        count = 0
        with SgWriter(
            SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))
        ) as writer:
            writer.write_row(rec)
            count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
