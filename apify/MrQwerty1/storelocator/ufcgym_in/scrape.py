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
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_urls():
    r = session.get("https://ufcgym.in/locations.html", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='button gym-location__cta' and contains(@href, '.html')]/@href"
    )


def get_data(slug, sgw: SgWriter):
    page_url = f"https://ufcgym.in{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//a[@class='signature-ribbon__link']/text()")
    ).strip()
    raw_address = " ".join(
        "".join(
            tree.xpath("//li[@class='meta-info__item meta-info__item--address']/text()")
        )
        .replace(":", "")
        .split()
    )
    street_address, city, state, postal = get_international(raw_address)
    if "-" in city:
        city, postal = city.split("-")
    phone = (
        tree.xpath("//span[contains(text(), 'Phone')]/following-sibling::text()")[0]
        .replace(":", "")
        .strip()
    )

    text = "".join(tree.xpath("//a[contains(@href, 'map')]/@href"))
    latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    if "/@" in text:
        latitude, longitude = text.split("/@")[1].split(",")[:2]
    hours_of_operation = (
        "".join(
            tree.xpath("//span[contains(text(), 'Hours')]/following-sibling::text()")
        )
        .replace(": ", "")
        .strip()
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="IN",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://ufcgym.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
