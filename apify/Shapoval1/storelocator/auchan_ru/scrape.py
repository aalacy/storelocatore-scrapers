import ssl
import json
import logging

from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import traceback
import os
import pyppdf.patch_pyppeteer

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-RU:{}@proxy.apify.com:8000/"

locator_domain = "auchan.ru"
log = SgLogSetup().get_logger(logger_name=locator_domain)
pyppeteer_level = logging.WARNING
logging.getLogger("pyppeteer").setLevel(pyppeteer_level)
logging.getLogger("websockets.protocol").setLevel(pyppeteer_level)

ssl._create_default_https_context = ssl._create_unverified_context

# To fix - certificate verify failed
logging.info(f"pyppdf loaded: {pyppdf.patch_pyppeteer}")

start_url = "https://www.auchan.ru/shops/"


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        days = h.get("weekdays")
        opens = h.get("open_time")
        closes = h.get("close_time")
        line = f"{days} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(contents, sgw: SgWriter):

    jsblock = (
        contents.split("window.__INITIAL_STATE__ = ")[1].split("</script>")[0].strip()
    )
    js = json.loads(jsblock)

    for j in js["shops"]["shopsListAll"]:

        page_url = start_url
        location_name = j.get("name") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        location_type = j.get("store_format") or "<MISSING>"
        ad = "".join(j.get("address"))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = j.get("region").get("name")
        country_code = "RU"
        city = a.city or "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone_number")
        hours = j.get("opening_hours")

        hours_of_operation = get_hours(hours)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )
        sgw.write_row(row)


async def get_response(driver, url):
    page = await driver.newPage()
    await stealth(page)
    try:
        await page.goto(f"{url}", {"timeout": 30000, "waitUntil": "networkidle2"})
        await page.waitForNavigation({"waitUntil": "networkidle2"})
        await page._client.send("Network.getAllCookies")

    except Exception:
        await page._client.send("Network.clearBrowserCookies")
        await page._client.send("Network.clearBrowserCache")
        traceback.print_exc()
    else:
        html_content = await page.content()
        return html_content
    finally:
        await page._client.send("Network.clearBrowserCookies")
        await page._client.send("Network.clearBrowserCache")
        log.info("Page is closing")
        await page.close()


async def main():
    log.info("Crawling Started")
    tasks = []
    browser = await launch(
        headless=True,
        defaultViewport=False,
        args=[
            "--no-sandbox",
            "--start-maximized",
            '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36"',
        ],
        ignoreHTTPSErrors=True,
    )
    tasks.append(asyncio.create_task(get_response(browser, start_url)))

    for contents in asyncio.as_completed(tasks):
        content = await contents
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
            fetch_data(content, writer)

        await browser.close()
        log.info("Finished Data Grabbing!")


asyncio.get_event_loop().run_until_complete(main())
