from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.budni.de"
    api_url = "https://www.budni.de/api/infra/branches"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        slug = j.get("navigationPath")
        page_url = f"{locator_domain}{slug}"
        location_name = j.get("displayName") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "DE"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("location").get("lat") or "<MISSING>"
        longitude = j.get("location").get("lon") or "<MISSING>"
        hours = j.get("openingHours")
        tmp = []
        days = ["mo", "tu", "we", "th", "fr", "sa"]
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
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=location_type,
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
