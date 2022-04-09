from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = (
            str(h.get("startDay"))
            .replace("1", "Monday")
            .replace("2", "Tuesday")
            .replace("3", "Wednesday")
            .replace("4", "Thursday")
            .replace("5", "Friday")
            .replace("6", "Saturday")
            .replace("7", "Sunday")
        )
        opens = h.get("openTimeFormat")
        closes = h.get("closeTimeFormat")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://burgerking.be/"
    api_url = "https://stores.burgerking.be/api/v3/locations?fitAll=true&language=fr"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        a = j.get("address")
        slug = j.get("slug")
        page_url = f"https://stores.burgerking.be/fr/{slug}"
        location_name = j.get("name") or "<MISSING>"
        ad = a.get("fullAddress")
        street_address = (
            "".join(a.get("street")).replace(",", "").strip() or "<MISSING>"
        )
        state = "<MISSING>"
        postal = a.get("zipCode") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        city = a.get("locality") or "<MISSING>"
        store_number = j.get("externalId") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        try:
            phone = j.get("contact").get("phone") or "<MISSING>"
        except:
            phone = "<MISSING>"
        hours = j.get("businessHours") or "<MISSING>"
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
