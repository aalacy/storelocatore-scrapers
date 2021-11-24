from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day")
        opens = h.get("open")
        closes = h.get("close")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = ";".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.yankeecandle.com/"
    api_url = "https://storescontent.yankeecandle.com/searchQuery?radius=50000&lat=33.5973469&long=-112.1072528&storeType=2"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:
        slug = j.get("ctaUrl")
        page_url = f"https://www.yankeecandle.com{slug}"
        location_name = j.get("label")
        street_address = j.get("address")
        state = j.get("state").get("abbr")
        postal = "".join(j.get("zip"))
        country_code = "US"
        if not postal.isdigit():
            country_code = "CA"
        city = j.get("city")
        store_number = j.get("storeNumber") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours = j.get("regHours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)

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
