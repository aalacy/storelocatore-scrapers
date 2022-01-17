import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.farmersfridge.com/page-data/locations-map/page-data.json"
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
    for j in js["result"]["pageContext"]["fridgeAndWholesaleLocations"]:
        a = j.get("operationConfigs")
        b = j.get("locationConfigs")
        ad = a.get("address")
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        page_url = "https://www.farmersfridge.com/locations-map/"
        try:
            location_name = b.get("prettyName")
        except:
            location_name = "<MISSING>"
        try:
            location_type = "".join(b.get("accessTo")) + " " + "".join(j.get("type"))
        except:
            location_type = "".join(j.get("type"))

        if location_type == "DELIVERY":
            continue
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        if state.find(", USA") != -1:
            state = state.replace(", USA", "").strip()
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        if city.find(",") != -1:
            city = city.split(",")[0].strip()
        try:
            latitude = b.get("coordinates").get("latitude")
            longitude = b.get("coordinates").get("longitude")
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        try:
            hours_of_operation = (
                "".join(b.get("workHours"))
                .replace("{", "")
                .replace('"', "")
                .replace("[[", "")
                .replace("]]", ",")
                .replace("}", "")
                .replace(",,", ";")
                .replace(", ", "-")
                .replace(",", "")
                .replace("]-[", " ")
                .strip()
            )

        except:
            hours_of_operation = "<MISSING>"

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.farmersfridge.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
