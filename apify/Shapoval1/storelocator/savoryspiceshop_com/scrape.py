import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day")
        opens = h.get("open")
        closes = h.get("close")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.savoryspiceshop.com/"
    api_url = "https://twrbhpz6v5.execute-api.us-west-2.amazonaws.com/Prod/locations"

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        a = j.get("address")
        slug = j.get("id")
        page_url = f"https://www.savoryspiceshop.com/pages/locations/{slug}"
        location_name = j.get("location_title")
        ad = f"{a.get('line_01')} {a.get('line_02')}".strip()
        try:
            b = usaddress.tag(ad, tag_mapping=tag)[0]
        except:
            ad = f"{a.get('line_02')}".strip()
            b = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = (
            f"{b.get('address1')} {b.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        street_address = (
            street_address.replace("Lincoln Square", "")
            .replace("Rockbrook Village", "")
            .strip()
        )
        state = a.get("state_code") or "<MISSING>"
        postal = a.get("postal_code") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        phone = a.get("phone")
        hours = j.get("store_hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)

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
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
