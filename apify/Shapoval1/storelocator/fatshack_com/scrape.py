import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.fatshack.com"
    page_url = "https://www.fatshack.com/locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="flex-col-locations w-dyn-item"]')
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
    for d in div:

        line = (
            " ".join(
                d.xpath(
                    './/div[@class="flex-col-address-wrapper-locations"]/a[contains(@href, "goo")]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        line = " ".join(line.split())
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            continue
        city = a.get("city") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        phone = (
            " ".join(
                d.xpath(
                    './/div[@class="flex-col-address-wrapper-locations"]/a[contains(@href, "tel")]//text()'
                )
            )
            or "<MISSING>"
        )
        country_code = "US"
        location_name = "".join(
            d.xpath('.//h4[@class="flex-col-heading-locations"]/text()')
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[@class="flex-col-hours-text-locations w-richtext"]/p//text()'
                )
            )
            .replace("\n", "")
            .replace(" â ", "-")
            .replace(" â", ";")
            .replace(" â", "")
            .replace("  Â ", "")
            .replace(" Â ", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        location_type = "<MISSING>"
        if "COMING SOON" in location_name:
            location_type = "Coming Soon"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=line,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
