from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_urls():
    urls = []

    for i in range(1, 100):
        r = session.get(
            f"https://tomntoms.com/eng/store/global_store_search.html?page={i}"
        )
        tree = html.fromstring(r.text)
        urls += tree.xpath('//a[.//span[contains(text(), "View")]]/@href')

        if len(urls) % 10 != 0:
            break

    return urls


def get_data(url, sgw: SgWriter):
    page_url = f"{locator_domain}{url.replace('..', '')}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = "".join(
        tree.xpath('//div[contains(text(), "Address")]/following-sibling::div/text()')
    )
    adr = parse_address(International_Parser(), line)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or SgRecord.MISSING
    )

    if len(street_address) < 5:
        street_address = line.split(",")[0].strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING
    country_code = adr.country or SgRecord.MISSING
    if len(state) == 2:
        country_code = "US"
    store_number = page_url.split("=")[-1].strip()
    location_name = "".join(tree.xpath('//p[@class="tit"]/text()'))
    phone = (
        "".join(
            tree.xpath('//div[contains(text(), "Tel")]/following-sibling::div/text()')
        )
        .replace("\n", "")
        .replace("TBA", "")
        .strip()
        or SgRecord.MISSING
    )
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "center")]/text()'))
        .split("LatLng(")[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "center")]/text()'))
        .split("LatLng(")[1]
        .split(",")[1]
        .split(")")[0]
        .strip()
    )
    hours_of_operation = (
        "".join(
            tree.xpath('//div[contains(text(), "Open")]/following-sibling::div/text()')
        )
        .replace("\n", "")
        .replace("~", "-")
        .strip()
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
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
    locator_domain = "https://tomntoms.com/eng"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
