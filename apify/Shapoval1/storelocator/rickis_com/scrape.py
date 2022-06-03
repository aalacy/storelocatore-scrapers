import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rickis.com"
    api_url = "https://www.rickis.com/on/demandware.store/Sites-rickis-Site/default/Stores-GetNearestStores?latitude=51.04473309999999&longitude=-114.0718831&countryCode=CA&distanceUnit=km&maxdistance=10000"
    r = session.get(api_url)
    r = r.text.replace('{"stores": ', "").replace("}}", "}")
    js = json.loads(r)
    for j in js.values():

        store_number = j.get("ID")
        street_address = (
            f"{j.get('address1')} {j.get('address2')}".replace("Unit 4 -", "")
            .replace("Unit L-045 -", "")
            .replace("Unit 11/12/13", "")
            .strip()
            or "<MISSING>"
        )
        if street_address.find(",") != -1:
            street_address = " ".join(street_address.split(",")[1:]).strip()
        phone = j.get("phone") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        country_code = j.get("countryCode")
        page_url = "https://www.rickis.com/on/demandware.store/Sites-rickis-Site/default/Stores-Find"
        location_name = j.get("name") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        hours = j.get("storeHours")
        hours_of_operation = "<MISSING>"
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split())
                .replace("TEMPORARILY CLOSED", "")
                .strip()
            )
        location_type = "<MISSING>"
        if str(store_number).find("TEMPORARILY CLOSED") != -1:
            location_type = str(store_number).split("-")[1].strip()
            store_number = str(store_number).split("-")[0].strip()

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
            raw_address=f"{j.get('address1')} {j.get('address2')} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
