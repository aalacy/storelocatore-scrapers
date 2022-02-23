from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("openingHours").get("dayType")
        try:
            opens = f"{h.get('openingHours').get('from1').get('hourOfDay')}:{h.get('openingHours').get('from1').get('minute')}{h.get('openingHours').get('from1').get('second')}"
        except:
            opens = "Closed"
        try:
            closes = f"{h.get('openingHours').get('to1').get('hourOfDay')}:{h.get('openingHours').get('from1').get('minute')}{h.get('openingHours').get('from1').get('second')}"
        except:
            closes = "Closed"
        line = f"{day} {opens} - {closes}"
        if opens == closes:
            line = f"{day} Closed"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spar.si/"
    api_url = "https://www.spar.si/trgovine/_jcr_content.stores.v2.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug = j.get("pageUrl")
        page_url = f"https://www.spar.si{slug}"
        location_name = j.get("name")
        street_address = j.get("address")
        state = "<MISSING>"
        postal = j.get("zipCode")
        country_code = "SI"
        city = j.get("city")
        store_number = "".join(j.get("locationId")).replace('"', "").strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("telephone")
        hours = j.get("shopHours") or "<MISSING>"
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
