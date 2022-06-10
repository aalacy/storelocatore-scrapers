from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day")
        time = h.get("day_hours")
        line = f"{day} {time}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "http://foosacklys.net/"
    api_url = "http://foosacklys.net/wp-json/restaurants/all"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        ad = (
            "".join(j.get("address"))
            .replace(", USA", "")
            .replace(", United States", "")
            .replace("N.", "N.,")
        )
        page_url = "http://foosacklys.net/restaurants/"
        location_name = j.get("locationName") or "<MISSING>"
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = "<MISSING>"
        if ad.split()[-1].isdigit():
            postal = ad.split()[-1]
        country_code = "US"
        city = ad.split(",")[1].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        phone = j.get("storeInfo").get("phone") or "<MISSING>"
        hours = j.get("hours")[1].get("hours_set") or "<MISSING>"
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
            store_number=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
