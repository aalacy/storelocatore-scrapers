import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.book-warehouse.com/"
    api_url = "https://app.locatedmap.com/initwidget/?instanceId=1987cb94-e8b4-4d54-90dd-219799f7bb0e&compId=comp-jcta7uxd&viewMode=json&styleId=style-jr7yn9r0"
    session = SgRequests()
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
    jsblock = (
        r.text.split('"mapSettings":"')[1]
        .split('","categories"')[0]
        .replace("\\", "")
        .replace("null", "None")
        .replace("true", "True")
        .replace("false", "False")
        .strip()
    )
    js = eval(jsblock)
    js_main = js[0]

    for j in js_main["fields"]["unpublishedLocations"]:
        unit = "".join(j.get("unit"))
        page_url = "https://www.book-warehouse.com/locations"
        location_name = (
            "".join(j.get("name")).replace("u00a0", "").strip() or "<MISSING>"
        )
        try:
            stci = (
                location_name.split("of")[1]
                .replace("LLC", "")
                .replace(", Inc.", "")
                .replace("Inc", "")
                .replace("Book", "")
                .replace("San Marcos", "San Marcos,")
                .replace("1", ",")
                .replace("New York,", "New York, NY")
                .strip()
            )
        except:
            stci = (
                location_name.split("Warehouse")[0]
                .replace("Book", "")
                .replace("San Marcos", "San Marcos,")
                .replace("1", ",")
                .strip()
            )

        ad = "".join(j.get("formatted_address"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        b = usaddress.tag(stci, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address.find(f"{unit}") == -1:
            street_address = street_address + " " + unit
        street_address = street_address.replace("u00a0", "").strip()
        city = a.get("city") or b.get("city") or "<MISSING>"
        if city == "<MISSING>" and stci.find(",") != -1:
            city = stci.split(",")[0].strip()
        state = a.get("state") or b.get("state") or "<MISSING>"
        if state == "<MISSING>" and stci.find(",") != -1:
            state = stci.split(",")[1].strip()
        if location_name == "Book Warehouse of Michigan, Inc.":
            state = "Michigan"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = "".join(j.get("tel")).replace("u00a0", "").strip() or "<MISSING>"
        hours_of_operation = j.get("opening_hours") or "<MISSING>"

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
