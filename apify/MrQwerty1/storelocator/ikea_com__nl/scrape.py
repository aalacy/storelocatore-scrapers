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
    city = adr.city or SgRecord.MISSING
    state = adr.state
    postal = adr.postcode or SgRecord.MISSING

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://www.ikea.com/nl/en/stores/")
    tree = html.fromstring(r.text)

    return tree.xpath("//h2/following-sibling::p/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = ", ".join(
        tree.xpath("//p[./strong[contains(text(), 'IKEA ')]]/text()")
    ).strip()
    street_address, city, state, postal = get_international(raw_address)
    street_address = raw_address.split(",")[0].strip()
    if city == SgRecord.MISSING:
        city = location_name.replace("IKEA ", "")

    if "(" in city:
        city = city.split("(")[0].strip()

    if postal == SgRecord.MISSING or len(postal) == 4:
        postal = " ".join(raw_address.split(",")[-1].split()[:2])

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    try:
        latitude = text.split("@")[1].split(",")[0]
        longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath(
        "//p[./strong[contains(text(), 'Opening') and not(contains(text(), 'holidays'))]]/text()|//p[./strong[contains(text(), 'Opening') and not(contains(text(), 'Click'))]]/following-sibling::p/text()"
    )
    hours = set(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="NL",
        store_number=SgRecord.MISSING,
        phone=SgRecord.MISSING,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=13) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.ikea.com/nl"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
