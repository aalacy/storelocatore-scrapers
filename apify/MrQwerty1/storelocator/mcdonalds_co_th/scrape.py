from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
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
    urls = []
    coords = dict()
    r = session.get("https://www.mcdonalds.co.th/storeLocations")
    tree = html.fromstring(r.text)
    elements = tree.xpath("//a[@class='store-container gray-bg']")
    for el in elements:
        urls.append("".join(el.xpath("./@href")))
        _id = "".join(el.xpath("./@data-store-id"))
        lat = "".join(el.xpath("./@data-lat"))
        lng = "".join(el.xpath("./@data-lng"))
        coords[_id] = (lat, lng)

    return urls, coords


def get_data(page_url, coords, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    store_number = page_url.split("/")[-1]
    location_name = "".join(tree.xpath("//div[@class='details-title']/text()")).strip()
    raw_address = "".join(
        tree.xpath("//div[@class='store-address contact-row']//text()")
    ).strip()
    street_address, city, state, postal = get_international(raw_address)
    phone = (
        "".join(tree.xpath("//div[@class='store-phone contact-row']//text()"))
        .lower()
        .replace("none", "")
        .strip()
    )
    latitude, longitude = coords.get(store_number) or (
        SgRecord.MISSING,
        SgRecord.MISSING,
    )
    hours_of_operation = "".join(
        tree.xpath("//div[@class='store-hour contact-row']//text()")
    ).strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="TH",
        store_number=store_number,
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
    urls, coords = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, url, coords, sgw): url for url in urls
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.mcdonalds.co.th/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
