from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://petvalu.com/"
    api_url = "https://store.petvalu.ca/modules/multilocation/?near_location=ON&threshold=400000&geocoder_components=country:CA&distance_unit=km&limit=2000000&services__in=&language_code=en-us&published=1&within_business=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["objects"]
    for j in js:

        location_name = j.get("location_name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("partner_location_sub_id")
        page_url = (
            j.get("location_url")
            or f"https://store.petvalu.ca/location/{store_number}/"
        )
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        phone = j.get("phonemap").get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("hours")[0].get("hours")
        tmp = []
        if hours:
            for h in range(len(hours)):
                day = (
                    str(h)
                    .replace("0", "Monday")
                    .replace("1", "Tuesday")
                    .replace("2", "Wednesday")
                    .replace("3", "Thursday")
                    .replace("4", "Friday")
                    .replace("5", "Saturday")
                    .replace("6", "Sunday")
                )
                opens = (
                    str(hours[h][0][0])
                    .replace(":00:00", ":00")
                    .replace(":30:00", ":30")
                    .strip()
                )
                closes = (
                    str(hours[h][0][1])
                    .replace(":00:00", ":00")
                    .replace(":30:00", ":30")
                    .strip()
                )
                line = f"{day} {opens} - {closes}"
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
            location_type=SgRecord.MISSING,
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
