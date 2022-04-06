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
    postal = adr.postcode or SgRecord.MISSING

    return postal


def get_urls():
    urls = set()
    r = session.get("https://www.habitat.eu/shop", headers=headers)
    root = html.fromstring(r.text)
    states = root.xpath("//div[@class='select-items select-hide']/a/@href")
    for state in states:
        req = session.get(f"https://www.habitat.eu{state}")
        tree = html.fromstring(req.text)
        links = tree.xpath("//a[contains(text(), 'Voir le magasin')]/@href")
        if not links:
            urls.add(f"https://www.habitat.eu{req.url.path}")
        for link in links:
            urls.add(f"https://www.habitat.eu{link}")

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'Store')]/text()")).strip()
    j = json.loads(text)

    location_name = j.get("name") or ""
    location_name = location_name.replace("&amp;", "&")
    raw_address = " ".join(
        " ".join(tree.xpath("//div[contains(@class, 'address')]/p[1]/text()")).split()
    )
    a = j.get("address")
    street_address = a.get("streetAddress") or ""
    street_address = street_address.replace("<br/>", " ")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = get_international(raw_address)
    country_code = page_url.split("/")[-2].upper()
    phone = (
        " ".join(
            " ".join(
                tree.xpath("//div[contains(@class, 'address')]/p[2]/text()")
            ).split()
        )
        .replace("-", "")
        .strip()
    )
    if ":" in phone:
        phone = phone.split(":")[-1].strip()
    store_number = j.get("branchCode")

    g = j.get("geo")
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    hours_of_operation = ";".join(
        tree.xpath("//p[@itemprop='openingHours']/@content")
    ).replace(", ", "-")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.habitat.eu/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
