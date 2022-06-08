import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.bigsandysuperstore.com/contacts", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//avb-link[contains(@data-href, '/locations/')]/@data-href")


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
    street_address = f"{adr1} {adr2}".strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = ", ".join(
        tree.xpath("//span[contains(@class, 'address-line')]/text()")
    ).strip()
    street_address, city, state, postal = get_address(raw_address)
    if not state and len(postal) == 7:
        state = postal[:2]
        postal = postal[2:]
    country_code = "US"
    phone = "".join(
        tree.xpath(
            "//span[contains(@class, 'fa-phone')]/following-sibling::*/text()|//span[contains(@class, 'fa-phone')]/following-sibling::text()"
        )
    ).strip()

    text = "".join(tree.xpath("//avb-link[contains(@data-href, 'google')]/@data-href"))
    if "/@" in text:
        latitude, longitude = text.split("/@")[1].split(",")[:2]
    else:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    location_type = "Superstore"
    if "outlet" in location_name.lower():
        location_type = "Outlet"
    if "-dublin" in page_url:
        location_type = "Superstore, Outlet"
    hours_of_operation = ";".join(
        tree.xpath("//h2[contains(text(), 'Hours')]/following-sibling::ul/li/text()")
    ).replace(" ;", ";")
    if ";Loc" in hours_of_operation:
        hours_of_operation = hours_of_operation.split(";Loc")[0].strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        location_type=location_type,
        locator_domain=locator_domain,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.bigsandysuperstore.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
