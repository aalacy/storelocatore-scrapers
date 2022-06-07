import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from typing import List


def get_urls():
    r = session.get("https://elpolloinka.com/")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@class='locations']/li/a/@href")


def get_address(line):
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    adr1 = a.get("address1") or ""
    adr2 = a.get("address2") or ""
    if "," in adr2:
        adr2 = adr2.split(",")[0].strip()
    street_address = f"{adr1} {adr2}".strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_exception(slug, sgw: SgWriter):
    page_url = f"{slug}/locations/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    d = tree.xpath("//div[./div[@class='main-location']]")[0]
    location_name = "".join(d.xpath(".//h2/text()")).strip()
    raw_address = "".join(
        d.xpath(".//p[./a[contains(@href, 'tel:')]]/text()[1]")
    ).strip()
    street_address, city, state, postal = get_address(raw_address)
    phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]//text()")).strip()

    text = "".join(d.xpath(".//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = d.xpath("//p[./a[contains(@href, 'tel:')]]/strong")
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
        _tmp.append(f"{day} {inter}")
    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def get_data(page_url, sgw: SgWriter):
    if "/location" not in page_url:
        get_exception(page_url, sgw)
        return
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h2[@class='heading']//text()")).strip()
    line = tree.xpath("//p[@class='address']/text()")
    raw = list(filter(None, [l.strip() for l in line]))  # type: List
    raw_address = ", ".join(raw)

    street_address = ", ".join(raw[:-1]).strip()
    line = raw[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    phone = "".join(tree.xpath("//p[@class='address']/a/text()")).strip()

    text = "".join(tree.xpath("//div[@class='map']/iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    hours = tree.xpath("//div[@class='hours']/p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
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
    locator_domain = "https://elpolloinka.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
