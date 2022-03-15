from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
import usaddress


def get_urls():
    r = session.get("https://www.twistedrootburgerco.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//h2/a[not(contains(@href, 'coming-soon'))]/@href")


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

    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = SgRecord.MISSING
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
    except usaddress.RepeatedLabelError:
        street_address = line.split(",")[0].strip()
        city = line.split(",")[1].strip()
        state, postal = line.split(",")[-1].strip().split()

    return street_address, city, state, postal


def get_data(url, sgw: SgWriter):
    page_url = f"https://www.twistedrootburgerco.com{url}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).strip()
    if "-" in location_name:
        location_name = location_name.split("-")[0].strip()

    raw_address = tree.xpath(
        "//h2[text()='Location']/following-sibling::div[1]//text()"
    )
    phone = ""
    if len(raw_address) > 1:
        phone = raw_address.pop()

    if "CALL" in phone:
        phone = phone.split("CALL")[-1].strip()
    if "@" in phone:
        phone = SgRecord.MISSING

    if "Call " in raw_address:
        raw_address.pop(raw_address.index("Call "))

    raw_address = ", ".join(raw_address)
    street_address, city, state, postal = get_address(raw_address)
    country_code = "US"

    hours_of_operation = ";".join(
        tree.xpath("//h2[text()='Hours']/following-sibling::div[1]//text()")
    )

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
    locator_domain = "https://www.twistedrootburgerco.com/"
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
