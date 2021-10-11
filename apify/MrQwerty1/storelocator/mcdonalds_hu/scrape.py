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
    if len(street_address) < 5:
        street_address = line.split(",")[0].strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://www.mcdonalds.hu/ettermeink")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='restaurants__more']/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.mcdonalds.hu{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = ", ".join(tree.xpath("//h1/text()|//h1/following-sibling::p/text()"))
    street_address, city, state, postal = get_international(line)
    country_code = "HU"

    phone = SgRecord.MISSING
    text = "".join(tree.xpath("//a[@class='js-dir-link']/@data-location"))
    try:
        latitude, longitude = text.split(",")
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//li[@class='is-active']//ul[@class='opening__days']/li/div")
    for h in hours:
        day = "".join(h.xpath("./div[1]/text()|./div[1]/b/text()")).strip()
        inter = "".join(h.xpath("./div[2]/text()|./div[2]/b/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.mcdonalds.hu"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
