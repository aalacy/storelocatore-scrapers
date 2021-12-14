import typing
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


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
    page_url = "https://www.keithssuperstores.com/store-location"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[contains(@class, 'dmTopContentRow')]//text()")
    divs = list(filter(None, [d.strip() for d in divs]))
    rows = []
    _tmp = []  # type: typing.List[str]

    for i, d in enumerate(divs):
        if "Food Shop:" in d:
            if i + 1 == len(divs):
                rows.append(_tmp)
                break
            else:
                continue

        if i + 1 == len(divs):
            _tmp.append(d)
            rows.append(_tmp)
            break

        if "Keith’s Superstores" in d:
            if _tmp:
                rows.append(_tmp)
            _tmp = [d]
            continue

        _tmp.append(d)

    for row in rows:
        location_name = row.pop(0)
        raw_address = row.pop(0)
        phone = row.pop(0).replace("Phone:", "").strip()
        hours_of_operation = ";".join(row).replace("Hours: ", "").replace("-;", "-")
        street_address, city, state, postal = get_address(raw_address)

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
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.keithssuperstores.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
