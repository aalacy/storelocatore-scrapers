from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from lxml import html
import asyncio
import logging
import os
from pyppeteer import launch
from pyppeteer_stealth import stealth
import traceback
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

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-RU:{}@proxy.apify.com:8000/"

# To fix - certificate verify failed: unable to get local issuer, we have used this library pyppdf
logging.info(f"pyppdf loaded: {pyppdf.patch_pyppeteer}")

logger = SgLogSetup().get_logger("currys_co_uk")

# Handling pyppeteer logging level
pyppeteer_level = logging.WARNING
logging.getLogger("pyppeteer").setLevel(pyppeteer_level)
logging.getLogger("websockets.protocol").setLevel(pyppeteer_level)


LOCATOR_URL = (
    "https://www.currys.co.uk/store-finder?showMap=true&horizontalView=true&isForm=true"
)
logger.info(f"LOCATOR URL for reference only: {LOCATOR_URL}")


API_ENDPOINT_URL = "https://api.currys.co.uk/store/api/stores?maxCount=5000&types=2in1-HS%2C2in1-MS%2C2in1-SS%2C3in1-HS%2C3in1-MS%2C3in1-SS%2CBLACK%2CCDG-HS%2CCUR-MS%2CCUR-SS%2CPCW-HS%2CPCW-SS"
DOMAIN = "currys.co.uk"


def fetch_data(content, sgw: SgWriter):
    logger.info("============================Content===============================")
    cont = content.split('{"payload"')[1]
    cont2 = cont.split("</pre></body></html>")[0]
    cont3 = '{"payload"' + cont2
    json_data = json.loads(cont3)
    logger.info(
        "======================Content Loaded with SUCCESS==============================="
    )
    js = json_data["payload"]["stores"]
    for j in js:
        street_address = j.get("address") or ""
        city = j.get("town") or ""
        state = ""
        postal = j.get("postcode") or ""
        country_code = "GB"
        store_number = j.get("id") or ""
        page_url = (
            f"https://www.currys.co.uk/gbuk/store-finder/london/store-{store_number}"
        )
        location_name = f"Currys PC World, {city}"
        phone = ""
        loc = j.get("location")
        latitude = loc.get("latitude") or ""
        longitude = loc.get("longitude") or ""
        location_type = ""

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours = j.get("standardOpeningHours") or []
        for h in hours:
            index = h.get("day") - 1
            day = days[index]
            start = h.get("from")
            close = h.get("to")
            _tmp.append(f"{day}: {start} - {close}")

        hours_of_operation = ";".join(_tmp) or ""
        item = SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address="",
        )
        sgw.write_row(item)


async def get_response(driver, url):
    try:
        page = await driver.newPage()
        await stealth(page)
        await page.goto(url)
        time.sleep(10)
        html_content = await page.content()
        return html_content
    finally:
        await page._client.send("Network.clearBrowserCookies")
        await page._client.send("Network.clearBrowserCache")
        logger.info("Page is closing")
        await page.close()


async def main():
    logger.info("Scrape Started")
    tasks = []
    browser = await launch(headless=True, args=["--no-sandbox"])
    tasks.append(asyncio.create_task(get_response(browser, API_ENDPOINT_URL)))
    for contents in asyncio.as_completed(tasks):
        content = await contents
        with SgWriter(
            SgRecordDeduper(
                SgRecordID(
                    {
                        SgRecord.Headers.STORE_NUMBER,
                        SgRecord.Headers.LATITUDE,
                        SgRecord.Headers.LONGITUDE,
                        SgRecord.Headers.STREET_ADDRESS,
                    }
                )
            )
        ) as writer:

            fetch_data(content, writer)

        await browser.close()
        logger.info("Finished Data Grabbing!")


asyncio.get_event_loop().run_until_complete(main())
