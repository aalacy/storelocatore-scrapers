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
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://www.ikea.gr/katastimata/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='store-item']/a[contains(@href, 'ikea')]/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.ikea.gr{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = " ".join(
        "".join(tree.xpath("//div[@class='gen-section'][1]/p[1]/text()")).split()
    )
    street_address, city, state, postal = get_international(raw_address)
    postal = postal.replace("TK ", "")

    phone = (
        "".join(tree.xpath("//div[@class='gen-section']/span/text()"))
        .replace("F:", "")
        .strip()
    )
    text = "".join(
        tree.xpath("//a[@class='button iconBtn s icon-link right blue']/@href")
    )
    if "=" in text:
        latitude, longitude = text.split("=")[-1].split(",")
    else:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath("//h3[text()='Καταστήματος']/following-sibling::p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GR",
        store_number=SgRecord.MISSING,
        phone=phone,
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

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.ikea.gr/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
