from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("schedule_day")
        opens = str(h.get("schedule_start"))
        closes = str(h.get("schedule_end"))
        line = f"{day} {opens} - {closes}".replace(":00:00", ":00").strip()
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hondaphil.com/"
    api_url = "https://www.hondaphil.com/api/dealers/all"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]
    for j in js:

        page_url = "https://www.hondaphil.com/dealer-finder"
        location_name = j.get("name")
        ad = j.get("address")
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address.isdigit():
            street_address = ad
        state = j.get("province_name")
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "Philippines"
        city = str(j.get("city_name")) or "<MISSING>"
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = str(j.get("contact_number")) or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        phone = (
            phone.replace("Globe:", "")
            .replace("Sales:", "")
            .replace("\n", "")
            .replace("Service", "")
            .strip()
        )
        if phone.find("to") != -1:
            phone = phone.split("to")[0].strip()
        hours_of_operation = "<MISSING>"
        hours = j.get("operating_hours") or "<MISSING>"
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
