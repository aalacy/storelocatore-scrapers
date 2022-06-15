import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.originalpenguin.com"
    api_url = "https://api.zenlocator.com/v1/apps/app_7tx9r8kr/locations/search?northeast=67.193746%2C31.935493&southwest=-26.135222%2C-180"

    session = SgRequests()
    r = session.get(api_url)

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

    js = r.json()
    for j in js["locations"]:

        page_url = "https://www.originalpenguin.com/pages/find-a-store"
        line = "".join(j.get("visibleAddress")).replace("\n", "").strip()
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{j.get('address1')} {j.get('address2')}".strip()
        city = j.get("city") or a.get("city") or "<MISSING>"
        postal = a.get("postal") or j.get("postcode") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        try:
            phone = j.get("contacts").get("con_c4g3q3jz").get("text")
        except AttributeError:
            phone = "<MISSING>"
        country_code = "US"
        location_name = j.get("name")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("hours")
        hours_of_operation = "<MISSING>"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        if "hoursOfOperation" in hours:
            for d in days:
                day = str(d).capitalize()
                time = hours.get("hoursOfOperation").get(f"{d}")
                line = f"{day} {time}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        r = session.get(
            "https://api.zenlocator.com/v1/apps/app_7tx9r8kr/init?widget=MAP"
        )
        js = r.json()["hours"]
        for j in js:
            hours_id = j.get("id")
            _tmp = []
            if hours_id == hours:
                for d in days:
                    day = str(d).capitalize()
                    time = j.get("hoursOfOperation").get(f"{d}")
                    line = f"{day} {time}"
                    _tmp.append(line)
                hours_of_operation = "; ".join(_tmp)

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
