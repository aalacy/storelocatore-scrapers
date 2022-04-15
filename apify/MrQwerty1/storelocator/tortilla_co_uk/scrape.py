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
    r = session.get("https://www.tortilla.co.uk/our-locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='GTM-Tracking-Header-locations-links']/@href")


def get_coords_from_text(text):
    try:
        lat, lng = text.split("/@")[1].split(",")[:2]
    except IndexError:
        lat, lng = SgRecord.MISSING, SgRecord.MISSING

    return lat, lng


def get_data(page_url, sgw: SgWriter):
    if "middleeast" in page_url:
        return
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    if tree.xpath("//div[@class='b-location-info-right-coming-soon-about']"):
        return

    location_name = "".join(
        tree.xpath("//div[@class='b-location-header-inner__title']/text()")
    ).strip()
    raw_address = "".join(
        tree.xpath("//span[text()='Contact']/following-sibling::p[1]//text()")
    ).strip()
    if "delivering" in raw_address.lower():
        raw_address = ""
    street_address, city, state, postal = get_international(raw_address)
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    latitude, longitude = get_coords_from_text(text)
    hours_of_operation = " ".join(
        ";".join(
            tree.xpath("//span[contains(text(), 'Hours')]/following-sibling::p/text()")
        ).split()
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GB",
        phone=phone,
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
    locator_domain = "https://www.tortilla.co.uk/"
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
