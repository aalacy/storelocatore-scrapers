from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.acecashexpress.com/"
    api_url = "https://www.acecashexpress.com/locations/assets/data/stores.json?origLat=37.09024&origLng=-95.712891&origAddress=United%20States&formattedAddress=%D0%A1%D0%BE%D0%B5%D0%B4%D0%B8%D0%BD%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5%20%D0%A8%D1%82%D0%B0%D1%82%D1%8B%20%D0%90%D0%BC%D0%B5%D1%80%D0%B8%D0%BA%D0%B8&boundsNorthEast=%7B%22lat%22%3A71.5388001%2C%22lng%22%3A-66.885417%7D&boundsSouthWest=%7B%22lat%22%3A18.7763%2C%22lng%22%3A170.5957%7D"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug = j.get("permalink") or "<MISSING>"
        page_url = f"https://www.acecashexpress.com{slug}"
        location_name = "ACE Cash Express"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("state_code") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("store_number") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        if latitude == "0.000000000000":
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for d in days:
            day = d
            opens = j.get(f"open_{d}")
            closes = j.get(f"close_{d}")
            line = f"{day} {opens} - {closes}"
            if opens == closes:
                line = f"{day} Closed"
            tmp.append(line)
        hours_of_operation = (
            " ;".join(tmp)
            .replace("00", ":00")
            .replace("1:000", "10:00")
            .replace("2:000", "20:00")
            or "<MISSING>"
        )
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        if phone == "0":
            phone = "<MISSING>"
        status = j.get("status")
        if status == "C":
            continue

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
