from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nordsee.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    data = {
        "type": "2001",
    }
    r = session.post("https://www.nordsee.com/de/", headers=headers, data=data)
    js = r.json()["stores"]
    for j in js:

        page_url = "https://www.nordsee.com/de/filialen/"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street_no") or "<MISSING>"
        postal = j.get("zipcode") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("uid") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        hours = j.get("opening")
        tmp = []
        hours_of_operation = "<MISSING>"
        if hours:
            for d in days:
                day = str(d).capitalize()
                times = hours.get(f"{d}")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=SgRecord.MISSING,
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
