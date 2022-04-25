from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://am-best.com/"
    api_url = "https://am-best.com/API/AMBest.Locations/Service/GetStops?moduleID=574&latitude=&longitude="
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        location_name = "AMBEST"
        if j.get("Color") == "green":
            location_name = "AMBEST Express"
        if j.get("Color") == "orange":
            location_name = "AMBEST Fuel Stop"
        if j.get("Color") == "blue":
            location_name = "AMBEST Travel Center/AMBEST Service Center"
        if j.get("Color") == "white":
            location_name = "AMBEST Service Center/Mobile Locations"
        if j.get("Color") == "red":
            location_name = "AMBEST Travel Center"
        street_address = j.get("Location") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Zip") or "<MISSING>"
        country_code = "US"
        city = j.get("City") or "<MISSING>"
        store_number = j.get("ID")
        page_url = (
            f"https://am-best.com/Travel-Centers/Location-Map?stopid={store_number}"
        )
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
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
            store_number=store_number,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
