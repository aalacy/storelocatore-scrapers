import re
import json
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="blacks_co_uk")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

MAX_WORKERS = 2


def get_store_urls():
    sl = "https://www.blacks.co.uk/stores"
    s1 = SgRequests(
        proxy_country="gb",
    )

    r1 = s1.get(sl, headers=headers)
    sel = html.fromstring(r1.text, "lxml")
    storeurls = sel.xpath('//a[contains(@href, "/stores/")]/@href')
    stores = ["https://www.blacks.co.uk" + i for i in storeurls]
    return stores


def fetch_records(idx, page_url, sgw: SgWriter):
    logger.info(f"PullingContentFrom: {page_url}")
    session = SgRequests(
        proxy_country="gb",
    )
    r = session.get(page_url, headers=headers)
    logger.info(f"{idx} HTTPStatusCode: {r.status_code} | {page_url}")
    sel_main = html.fromstring(r.text, "lxml")

    yextpage_url = sel_main.xpath(
        '//script[contains(@src, "wNKqj2lKTBGDTDiyrrzl_SCAFzdpolUkrUzjNBtf19FQLoDqvgV7Zq6nkg9b1ue")]/@src'
    )[0]
    logger.info(f"[{idx}] Data URL: {yextpage_url}")
    location_id = yextpage_url.split("location_id=")[-1]
    if not location_id:
        return
    session1 = SgRequests(
        proxy_country="gb",
    )
    r1 = session1.get(yextpage_url, headers=headers)
    js = json.loads(r1.text.split("Yext._embed(")[-1].rstrip(")"))
    js_schema = js["entities"][0]["schema"]
    data = js_schema
    location_name = sel_main.xpath("//title/text()")[0].split("|")[1].strip()
    address = data["address"]
    street_address = address["streetAddress"]
    city = address["addressLocality"]
    postal = address["postalCode"]
    country_code = "GB"
    geo = data["geo"]
    latitude = geo["latitude"]
    longitude = geo["longitude"]
    phone = data["telephone"]

    hours = []
    for hour in data["openingHoursSpecification"]:
        day = re.sub("http://schema.org/", "", hour["dayOfWeek"])
        opens = ""
        closes = ""
        if "opens" in hour:
            opens = hour["opens"]
        if "closes" in hour:
            closes = hour["closes"]
        oc = ""
        if not opens and not closes:
            oc = "Closed"
        else:
            oc = f"{opens}-{closes}"
        hours.append(f"{day}: {oc}")

    hours_of_operation = "; ".join(hours)

    item = SgRecord(
        locator_domain="blacks.co.uk",
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=location_id,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        phone=phone,
        raw_address=f"{street_address}, {city}, {postal}",
    )
    sgw.write_row(item)
    logger.info(f"ITEM: {item.as_dict()}\n")


def fetch_data(sgw: SgWriter):
    loc_url_list = get_store_urls()
    logger.info(f"Total GB stores: {len(loc_url_list)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_gb = [
            executor.submit(fetch_records, idx, url, sgw)
            for idx, url in enumerate(loc_url_list[0:])
        ]
        tasks.extend(task_gb)
        for future in as_completed(tasks):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":

    scrape()
