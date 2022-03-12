import ssl
import time
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome


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


def fetch_data(sgw: SgWriter):
    page_url = "https://www.leboulangercafe.com/locations"
    with SgChrome() as fox:
        fox.get(page_url)
        time.sleep(3)
        source = fox.page_source

    tree = html.fromstring(source)
    divs = tree.xpath("//div[@class='w-cell row' and .//h2]")

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        line = d.xpath(".//div/p/text()")
        raw_address = line.pop(0)
        hours_of_operation = line.pop(0).replace("Hours:", "").strip()
        street_address, city, state, postal = get_address(raw_address)
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/@href")).replace(
            "tel:", ""
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.leboulangercafe.com/"
    ssl._create_default_https_context = ssl._create_unverified_context
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
