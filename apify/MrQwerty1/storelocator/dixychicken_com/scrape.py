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

    return street_address, city, state, postal


def get_urls():
    r = session.get("http://dixychicken.com/locatestore.html")
    tree = html.fromstring(r.text)

    return tree.xpath("//td/a/@href")


def get_data(page_url, sgw: SgWriter):
    if "construction" in page_url or "about" in page_url:
        return
    if not page_url.startswith("http"):
        page_url = f"{locator_domain}{page_url}"
    r = session.get(page_url)
    if r.status_code == 404:
        return

    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//h1/text()")).strip()
    lines = tree.xpath("//h1/following-sibling::p/text()")
    lines = list(filter(None, [line.strip() for line in lines]))
    phone = lines.pop().replace("Ph:", "").strip()

    raw_address = " ".join(lines)
    street_address, city, state, postal = get_international(raw_address)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="NZ",
        phone=phone,
        locator_domain=locator_domain,
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
    locator_domain = "http://dixychicken.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
