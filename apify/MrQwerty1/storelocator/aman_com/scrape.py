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
    state = adr.state
    postal = adr.postcode
    country = adr.country

    return street_address, city, state, postal, country


def get_urls():
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='destination-quick-links']//a[@class='clean']/@href"
    )


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.aman.com{slug}"
    r = session.get(page_url)
    if r.status_code == 403:
        return
    tree = html.fromstring(r.text)
    d = tree.xpath("//div[@class='grid grid--start']")[0]

    location_name = "".join(d.xpath(".//h3/text()")).strip()
    raw_address = " ".join("".join(d.xpath(".//address[not(./a)]/text()")).split())
    iscoming = tree.xpath(
        "//h1/preceding-sibling::p[contains(text(), 'Opening') or contains(text(), 'OPENING')]"
    )
    if "Opening" in raw_address or "Coming" in raw_address or iscoming:
        return
    street_address, city, state, postal, country_code = get_international(raw_address)
    if not city:
        city = SgRecord.MISSING
    if city[0].isdigit():
        postal = city
        city = SgRecord.MISSING
    if city[-1].isdigit():
        postal = city.split()[-1]
        city = city.replace(postal, "").strip()
    try:
        phone = d.xpath(".//a[contains(@href, 'tel:')]/text()")[0].strip()
    except IndexError:
        phone = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        locator_domain=locator_domain,
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
    locator_domain = "https://www.aman.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
