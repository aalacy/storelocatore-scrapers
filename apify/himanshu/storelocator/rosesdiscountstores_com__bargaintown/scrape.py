import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rosesdiscountstores.com"
    api_url = "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?countryCode=US&name=Bargain%20Town&query=Bargain%20Town&radius=80467"
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
    js = r.json()

    for j in js["locations"]:
        page_url = "https://www.rosesdiscountstores.com/#bargaintown"
        location_name = j.get("name") or "<MISSING>"
        location_type = "<MISSING>"

        ad = "".join(j.get("address"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        try:
            phone = j.get("contacts").get("con_wg5rd22k").get("text")
        except AttributeError:
            phone = "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        try:
            hours = j.get("hours").get("hoursOfOperation")
        except AttributeError:
            hours = "<MISSING>"
        hours_id = j.get("hours")
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = f"MON {hours.get('mon')} TUE {hours.get('tue')} WED {hours.get('wed')} THU {hours.get('thu')} FRI {hours.get('fri')} SAT {hours.get('sat')} SUN {hours.get('sun')}"
        if hours_of_operation == "<MISSING>":
            r = session.get(
                "https://api.zenlocator.com/v1/apps/app_vfde3mfb/init?widget=MAP"
            )
            js = r.json()["hours"]
            for j in js:
                hrs_id = j.get("id")
                if hrs_id == hours_id:
                    a = j.get("hoursOfOperation")
                    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                    tmp = []
                    for d in days:
                        day = d
                        time = a.get(f"{d}")
                        line = f"{day} {time}"
                        tmp.append(line)
                    hours_of_operation = "; ".join(tmp)

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
