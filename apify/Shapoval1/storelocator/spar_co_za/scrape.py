from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spar.co.za"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.spar.co.za/Store-Finder",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.spar.co.za",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = '{"SearchText":"","Types":[],"Services":[],"IncludedProvinceIds":[1,2,3,4,5,6,7,8,9,10,11,12,13]}'

    r = session.post(
        "https://www.spar.co.za/api/stores/search", headers=headers, data=data
    )
    js = r.json()
    for j in js:

        slug = j.get("Alias")
        page_url = f"https://www.spar.co.za/Home/Store-View/{slug}"
        location_name = j.get("Name") or "<MISSING>"
        location_type = j.get("Type") or "<MISSING>"
        ad = f"{j.get('PhysicalAddress')} {j.get('Town')}".strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        country_code = "ZA"
        city = a.city or "<MISSING>"
        store_number = j.get("Id")
        latitude = j.get("GPSLat") or "<MISSING>"
        longitude = j.get("GPSLong") or "<MISSING>"
        phone = str(j.get("TelephoneNumber")).strip() or "<MISSING>"
        hours_of_operation = (
            f"Mon to Fri {j.get('TradingHoursMonToFriOpen')} - {j.get('TradingHoursClose')} Sat {j.get('TradingHoursSatOpen')} - {j.get('TradingHoursSatClose')} Sun {j.get('TradingHoursSunOpen')} - {j.get('TradingHoursSunClose')}".strip()
            or "<MISSING>"
        )
        if hours_of_operation == "Mon to Fri  -  Sat  -  Sun  -":
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Sun  -") != -1:
            hours_of_operation = hours_of_operation.replace("Sun  -", "Sun  Closed")
        if hours_of_operation.find("unfortunately closed") != -1:
            hours_of_operation = "Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
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
