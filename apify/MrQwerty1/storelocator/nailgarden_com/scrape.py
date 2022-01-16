import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.nailgarden.com")
    tree = html.fromstring(r.text)

    return set(
        tree.xpath(
            "//a[contains(text(), 'Locations')]/following-sibling::div//a[not(contains(text(), 'Coming'))]/@href"
        )
    )


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


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.nailgarden.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//div[@class='sqs-block-content' and ./pre and ./p]/p/text()")
    location_name = "".join(
        tree.xpath(
            "//div[@class='sqs-block-content' and ./pre and ./p]/pre/code/text()"
        )
    ).strip()
    phone = line.pop()
    raw_address = line.pop(0).replace("\xa0", "")
    if "Hours" in line:
        line.remove("Hours")
    hours_of_operation = ";".join(line)
    street_address, city, state, postal = get_address(raw_address)

    try:
        text = tree.xpath("//div[@data-block-json]/@data-block-json")[0]
        j = json.loads(text)["location"]
        latitude = j.get("markerLat")
        longitude = j.get("markerLng")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

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

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.nailgarden.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
