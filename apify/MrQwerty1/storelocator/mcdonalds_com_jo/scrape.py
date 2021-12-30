from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, city):
    if city:
        adr = parse_address(International_Parser(), line, city=city)
    else:
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
    urls = []

    for i in range(1, 500):
        r = session.get(f"https://mcdonalds.com.jo/locations?page={i}")
        tree = html.fromstring(r.text)
        _tmp = tree.xpath("//a[@class='btn btn-red' and contains(@href, '.jo')]/@href")
        urls += _tmp
        if len(_tmp) < 9:
            break

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = ", ".join(tree.xpath("//div[@class='city']/following-sibling::p/text()"))
    city = "".join(tree.xpath("//div[@class='city']/text()")).strip() or ""
    street_address, city, state, postal = get_international(line, city)
    country_code = "JO"
    text = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.LatLng')]/text()")
    )
    latitude, longitude = eval(text.split("new google.maps.LatLng")[1].split(";")[0])

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=SgRecord.MISSING,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=SgRecord.MISSING,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://mcdonalds.com.jo/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
