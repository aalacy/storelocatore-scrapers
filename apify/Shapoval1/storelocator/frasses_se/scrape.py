from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://frasses.se"
    api_url = "https://frasses.se/api/restaurants/init"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        location_name = j.get("title") or "<MISSING>"
        ad = str(j.get("address")).replace("03 54,", "03 54") or "<MISSING>"
        location_type = j.get("post_type") or "<MISSING>"
        street_address = ad.split(",")[0].strip()
        postal = " ".join(ad.split(",")[1].split()[:-1]).strip()
        country_code = "SE"
        city = ad.split(",")[1].split()[-1].strip()
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        page_url = f"https://frasses.se/#!/restauranger/{str(location_name).lower()}/{store_number}"
        phone = j.get("telephone") or "<MISSING>"
        if str(phone).find(":") != -1:
            phone = str(phone).split(":")[1].strip()
        hours_of_operation = "<MISSING>"
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hours = j.get("open")
        tmp = []
        if hours:
            for d in days:
                day = d
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
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
