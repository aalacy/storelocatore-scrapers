import json
import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog


def get_tree(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    return tree


def get_urls():
    tree = get_tree("https://www.millets.co.uk/stores")
    return tree.xpath("//ul[contains(@id, 'brands_')]//a/@href")


def fetch_page_schema(url):
    tree = get_tree(url)
    src = tree.xpath("//script[contains(@src, 'yextpages.net')]/@src").pop()
    r = session.get(src)

    match = re.search(r"Yext._embed\((.*)\n?\)", r.text, re.IGNORECASE)
    if not match:
        logger.error("unable to parse")

    data = json.loads(match.group(1))
    entity = data["entities"].pop()
    return entity["schema"]


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.millets.co.uk{slug}"
    data = fetch_page_schema(page_url)

    a = data.get("address")
    street_address = a.get("streetAddress") or ""
    city = a.get("addressLocality") or ""
    if f", {city}" in street_address:
        street_address = street_address.split(f", {city}")[0].strip()
    postal = a.get("postalCode")
    country_code = "GB"

    location_name = f"{data.get('name')} {city}"
    store_number = data.get("@id")
    phone = data.get("telephone")

    geo = data.get("geo")
    latitude = geo.get("latitude")
    longitude = geo.get("longitude")
    location_type = (data.get("@type") or [SgRecord.MISSING]).pop()

    _tmp = []
    for time in data.get("openingHoursSpecification"):
        day = time["dayOfWeek"]
        opens = time.get("opens")
        closes = time.get("closes")
        if opens and closes:
            _tmp.append(f"{day}: {opens}-{closes}")

    hours_of_operation = ",".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.millets.co.uk/"
    logger = sglog.SgLogSetup().get_logger(logger_name="millets.co.uk")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
