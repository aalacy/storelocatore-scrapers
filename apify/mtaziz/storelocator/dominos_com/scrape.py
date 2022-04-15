from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import time
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
import random

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


MISSING = SgRecord.MISSING
DOMAIN = "dominos.com"
MAX_WORKERS = 14
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_com")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def get_us_store_urls():
    idx = 0
    locs = []
    states = []
    url = "https://pizza.dominos.com/sitemap.xml"
    r = get_response(idx, url)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines():
        if "https://pizza.dominos.com/" in line and "/home/sitemap" not in line:
            states.append(
                line.replace("\r", "").replace("\n", "").replace("\t", "").strip()
            )
    for idx2, state in enumerate(states):
        Found = True
        logger.info(("Pulling State %s..." % state))
        r2 = get_response(idx2, state)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines():
            if "https://pizza.dominos.com/" in line2:
                if line2.count("/") == 4:
                    Found = False
                if Found:
                    locs.append(
                        line2.replace("\r", "")
                        .replace("\n", "")
                        .replace("\t", "")
                        .strip()
                    )
        logger.info(("%s Locations Found..." % str(len(locs))))
    return locs


def fetch_records_us(idx, loc, sgw: SgWriter):
    try:

        r2 = get_response(idx, loc)
        sel = html.fromstring(r2.text, "lxml")
        raw_data = sel.xpath(
            '//script[contains(@type, "application/ld+json") and contains(text(), "LocalBusiness")]/text()'
        )
        raw_data1 = "".join(raw_data)
        try:
            json_data = json.loads(raw_data1)
        except json.decoder.JSONDecodeError:
            return
        page_url = json_data["url"]
        logger.info(f"[{idx}][US] Pulling the Data From: {page_url}")
        location_name = json_data["name"] or MISSING
        address = json_data["address"]
        street_address = address["streetAddress"] or MISSING
        city = address["addressLocality"] or MISSING
        state = address["addressRegion"] or MISSING
        zip_postal = address["postalCode"] or MISSING
        country_code = "US"
        store_number = json_data["branchCode"] or MISSING

        phone = ""
        try:
            phone = json_data["telephone"]
        except:
            phone = MISSING

        location_type = "Store"
        latitude = json_data["geo"]["latitude"] or MISSING
        longitude = json_data["geo"]["longitude"] or MISSING
        locator_domain = DOMAIN

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
        raw_address = MISSING
        location_name = location_name + " #" + str(store_number)
        rec = SgRecord(
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
        if rec is not None:
            sgw.write_row(rec)

    except Exception as e:
        raise Exception(f" Please fix this >> {e} >> Error Encountered at {loc}")


def fetch_data(sgw: SgWriter):
    us_store_urls = get_us_store_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records_us, unum, url, sgw)
            for unum, url in enumerate(us_store_urls[0:])
        ]
        tasks.extend(task_us)
        for future in as_completed(tasks):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
