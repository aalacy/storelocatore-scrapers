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
    for i in range(1, 48):
        r = session.get(f"https://www.mos.jp/shop/{str(i).zfill(2)}/", headers=headers)
        tree = html.fromstring(r.text)
        urls += tree.xpath("//div[@class='frame-green clickableFrame']/a/@href")

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.mos.jp{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//span[@class='hps-s2']/text()")).strip()
    raw_address = "".join(
        tree.xpath("//th[contains(text(), '住所')]/following-sibling::td/text()")
    ).strip()
    street_address, city, state, postal = get_international(raw_address)
    phone = "".join(
        tree.xpath("//th[contains(text(), 'TEL')]/following-sibling::td//text()")
    ).strip()
    text = "".join(tree.xpath("//iframe/@src"))
    try:
        latitude, longitude = text.split("q=")[1].split("&")[0].split(",")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    hours_of_operation = " ".join(
        ";".join(
            tree.xpath("//th[contains(text(), '営業時間')]/following-sibling::td//text()")
        ).split()
    )
    if hours_of_operation.startswith(";"):
        hours_of_operation = hours_of_operation[1:]
    if hours_of_operation.endswith(";"):
        hours_of_operation = hours_of_operation[:-1]

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="JP",
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

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.mos.jp/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
