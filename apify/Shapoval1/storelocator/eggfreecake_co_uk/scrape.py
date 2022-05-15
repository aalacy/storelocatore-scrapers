from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.eggfreecake.co.uk/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(
        "https://www.eggfreecake.co.uk/storelocator/ajax/stores?_=1642074936221",
        headers=headers,
    )
    js = r.json()
    for j in js:

        page_url = f"https://www.eggfreecake.co.uk/storelocator/{j.get('link')}"
        location_name = "".join(j.get("name"))
        street_address = (
            "".join(j.get("address"))
            .replace(",", "")
            .replace("Slough", "")
            .replace("Cardiff", "")
            .strip()
        )
        postal = j.get("postcode")
        country_code = "UK"
        city = (
            str(j.get("city")).replace("None", "").replace(",", "").strip()
            or "<MISSING>"
        )
        if city == "<MISSING>":
            city = location_name
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        store_number = j.get("store_code")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = str(j.get("phone")).replace("None", "").strip() or "<MISSING>"
        if phone.find("(") != -1:
            phone = phone.split("(")[0].strip()
        if phone.find(",") != -1:
            phone = phone.split(",")[0].split(":")[1].strip()
        if phone.find("Mobile") != -1:
            phone = phone.split("Mobile")[0].strip()
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
            opens = j.get(f"{d}_open")
            closes = j.get(f"{d}_close")
            line = f"{day} {opens} - {closes}"
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
