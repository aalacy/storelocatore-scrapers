import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://aeropostale.com/"
    api_url = "https://www.aeropostale.com/on/demandware.store/Sites-aeropostale-Site/default/Stores-GetNearestStores?latitude=40.75368539999999&longitude=-73.9991637&countryCode=US&distanceUnit=mi&maxdistance=500000"
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    r = session.get(api_url, headers=headers)
    js = json.loads(r.content)["stores"]
    for j in js.values():

        store_number = j.get("ID")
        page_url = f"https://www.aeropostale.com/storedetails/?StoreID={store_number}"
        location_name = j.get("name") or "<MISSING>"
        location_type = "<MISSING>"
        street_address = (
            f"{j.get('address1')} {j.get('address2')}".strip() or "<MISSING>"
        )
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours = j.get("storeHours")
        hours_of_operation = "<MISSING>"
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("This Location Is Open!") != -1:
            hours_of_operation = hours_of_operation.split("This Location Is Open!")[
                0
            ].strip()
        if hours_of_operation.find("This location is closed.") != -1:
            hours_of_operation = hours_of_operation.replace(
                "This location is closed.", ""
            ).strip()
            location_type = "Closed"
        if hours_of_operation.find("For your") != -1:
            hours_of_operation = hours_of_operation.split("For your")[0].strip()

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
