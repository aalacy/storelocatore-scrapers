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
    urls = []
    for i in range(1, 100):
        r = session.get(
            f"http://www.moskorea.kr/store/standard?area=&area2=&area2&text=&page={i}",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        urls += tree.xpath("//td/a[@class='btn']/@href")
        if len(tree.xpath("//td/a[@class='btn']/@href")) < 8:
            break

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"http://www.moskorea.kr/store/standard{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//strong[text()='매장명']/following-sibling::p/text()")
    ).strip()
    raw_address = "".join(
        tree.xpath("//strong[text()='주소']/following-sibling::p/text()")
    ).strip()
    street_address, city, state, postal = get_international(raw_address)
    phone = "".join(
        tree.xpath("//strong[text()='전화번호']/following-sibling::p/text()")
    ).strip()
    if phone == "-":
        phone = SgRecord.MISSING
    hours_of_operation = (
        tree.xpath("//div[@class='txt']/text()")[0]
        .replace("·", "")
        .replace("/", ";")
        .replace("~", "-")
        .strip()
    )
    if "(" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("(")[0].strip()
    if "-" not in hours_of_operation:
        hours_of_operation = SgRecord.MISSING
    store_number = slug.split("=")[-1]

    try:
        text = "".join(
            tree.xpath("//script[contains(text(), 'kakao.maps.LatLng')]/text()")
        )
        latitude, longitude = eval(text.split("kakao.maps.LatLng")[1].split(";")[0])
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="KR",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
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
    locator_domain = "http://www.moskorea.kr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
