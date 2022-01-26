from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("label")
        time = h.get("content")
        line = f"{day} {time}"
        tmp.append(line)
    hours_of_operation = ";".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://afcurgentcare.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(
        "https://www.afcurgentcare.com/modules/multilocation/?near_location=10001&threshold=20000&geocoder_region=&limit=20000&services__in=&language_code=en-us&published=1&within_business=true",
        headers=headers,
    )
    js = r.json()

    for j in js["objects"]:

        page_url = j.get("location_url") or "https://www.afcurgentcare.com/locations"
        location_name = j.get("location_name") or "<MISSING>"
        street_address = (
            f"{j.get('street')} {j.get('street2') or ''}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = j.get("country")
        phone = j.get("phonemap").get("phone") or "<MISSING>"
        latitude = j.get("lon") or "<MISSING>"
        longitude = j.get("lat") or "<MISSING>"
        hours = j.get("formatted_hours").get("primary").get("days") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        cms = j.get("custom_fields").get("finder_cta_label")
        if "Coming Soon" in str(cms):
            hours_of_operation = "Coming Soon"

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
