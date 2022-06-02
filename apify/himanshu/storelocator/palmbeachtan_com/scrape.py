from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://palmbeachtan.com/"
    api_url = "https://palmbeachtan.com/locations/srj/40.830167,-74.1298684/5000000/1000000/geo/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        slug = j.get("salon_url")
        location_name = j.get("salon_name") or "<MISSING>"
        street_address = j.get("salon_address") or "<MISSING>"
        state = j.get("salon_state") or "<MISSING>"
        page_url = f"https://palmbeachtan.com/locations/{state}/{slug}/"
        postal = j.get("salon_zip") or "<MISSING>"
        country_code = "US"
        city = j.get("salon_city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("salon_lat") or "<MISSING>"
        longitude = j.get("salon_lon") or "<MISSING>"
        phone = j.get("phone_1") or "<MISSING>"
        days = ["mon", "tue", "wen", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = str(d).capitalize()
            opens = j.get(f"{d}_open")
            closes = j.get(f"{d}_close")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
