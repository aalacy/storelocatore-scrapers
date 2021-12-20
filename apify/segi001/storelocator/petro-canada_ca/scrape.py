from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.petro-canada.ca/"
    api_url = "https://www.petro-canada.ca/en/api/petrocanada/locations?fuel&hours&lat=51.751959&limit=25000&lng=-108.855462&place&range=1000000000&service"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        street_address = j.get("AddressLine") or "<MISSING>"
        state = j.get("Subdivision") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "CA"
        city = j.get("PrimaryCity") or "<MISSING>"
        store_number = j.get("Id") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        page_url = f"https://www.petro-canada.ca/en/personal/gas-station-locations?latlng={latitude},{longitude}"
        phone = j.get("Phone") or "<MISSING>"
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        tmp = []
        for d in days:
            day = d
            opens = str(j.get("Hours").get(f"{d}OpenHr"))
            opens = opens[:2] + ":" + opens[2:]
            closes = str(j.get("Hours").get(f"{d}CloseHr"))
            closes = closes[:2] + ":" + closes[2:]
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
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
