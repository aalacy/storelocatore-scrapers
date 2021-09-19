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
    city = address["addressLocality"] or MISSING
    state = address["addressRegion"] or MISSING
    zip_postal = address["postalCode"] or MISSING
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


async def get_response_initial(url):
    driver = await launch(options)
    page = await driver.newPage()
    await stealth(page)
    await page.goto(url)
    await asyncio.sleep(5)
    html_content = await page.content()
    await driver.close()
    extract_task = asyncio.ensure_future(get_store_urls(html_content))
    extract_results = await asyncio.gather(extract_task)
    return extract_results


async def get_store_urls(html_content):
    geo = dict()
    urls = []
    tree = html.fromstring(html_content)
    logger.info(f"html content: {html_content}")
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
        logger.info(f"List of Store URLs: {urls}")
    return urls, geo


def get_urls():
    return asyncio.get_event_loop().run_until_complete(
        get_response_initial(LOCATION_URL)
    )


urls_geo = get_urls()


def main_generator():

    urls = urls_geo[0][0]
    geo = urls_geo[0][1]
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
