from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.popshelf.com/"
    api_url = "https://api.popshelf.com/api/stores/PROD/store?popkey=07a8b68d524c4ccea3c9a4dd546ba55d"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalcode") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("storenumber") or "<MISSING>"
        page_url = f"https://www.popshelf.com/store/{store_number}"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d.capitalize()
            time = j.get(f"hours_{d}")
            time = str(time).replace(":", "-").replace("00", ":00").strip()
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = ", ".join(tmp)

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
