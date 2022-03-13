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
    data = {"keyword": "", "cari": ""}
    r = session.post("https://www.cfcindonesia.com/index.php?page=peta", data=data)
    tree = html.fromstring(r.text)

    return tree.xpath("//td/a[contains(@href, 'map-')]/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"{locator_domain}{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//b[contains(text(), 'Store')]/following-sibling::text()[1]")
    ).strip()
    raw_address = "".join(
        tree.xpath("//b[contains(text(), 'Alamat')]/following-sibling::text()[1]")
    ).strip()
    street_address, city, state, postal = get_international(raw_address)
    text = "".join(tree.xpath("//script[contains(text(), 'var lonLat')]/text()"))
    try:
        longitude = text.split(".LonLat(")[1].split(",")[0].strip()
        latitude = text.split(".LonLat(")[1].split(",")[1].split(")")[0].strip()
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="ID",
        latitude=latitude,
        longitude=longitude,
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
    locator_domain = "https://www.cfcindonesia.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
