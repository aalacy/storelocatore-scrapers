import json
import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.galls.com"
    api_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/4051/stores.js?callback=SMcallback2"
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
    jsblock = r.text.split("SMcallback2(")[1].split("}]})")[0] + "}]}"
    js = json.loads(jsblock)
    for j in js["stores"]:

        page_url = "https://www.galls.com/pages/stores"
        location_name = j.get("name") or "<MISSING>"
        ad = j.get("address") or "<MISSING>"
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        if state.find(",") != -1:
            state = state.split(",")[0].strip()
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find("Fire:") != -1:
            phone = phone.split("Fire:")[1].split("<")[0].strip()
        hours_of_operation = (
            "".join(j.get("custom_field_2")).replace("<br>", " ").strip()
        )
        desc2 = "".join(j.get("custom_field_1")).replace("<br>", " ").strip()
        if "Fax" not in desc2:
            hours_of_operation = (
                f"{j.get('custom_field_1')} {j.get('custom_field_2')}".replace(
                    "<br>", " "
                ).strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("Not open to the general public", "")
            .replace("Miami PD Personnel Only", "")
            .strip()
        )
        if hours_of_operation.find("to visit") != -1:
            hours_of_operation = hours_of_operation.split("to visit")[1].strip()

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
