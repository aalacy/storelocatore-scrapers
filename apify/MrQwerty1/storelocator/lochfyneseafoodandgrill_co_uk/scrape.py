import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    postal = adr.postcode

    return street_address, city, postal


def get_urls():
    r = session.get("https://www.lochfyneseafoodandgrill.co.uk/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='pub-list__pub-name']/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.lochfyneseafoodandgrill.co.uk{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'BarOrPub')]/text()"))
    j = json.loads(text)

    location_type = j.get("@type")
    store_number = j.get("branchCode")
    location_name = j.get("name")
    hours = j.get("openingHours") or []
    hours_of_operation = ";".join(hours)

    raw_address = j.get("address")
    street_address, city, postal = get_international(raw_address)
    phone = j.get("telephone")

    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.lochfyneseafoodandgrill.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
