import json

from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, s=False, c=False, p=False):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    if s:
        return street

    if c:
        return city

    if p:
        return postal


def fetch_data(sgw: SgWriter):
    for i in range(1, 500):
        api = f"https://www.paul-bakeries.com/en/bakeries/storelocator/ajax/city/Johannesburg/input/johannesburg/country/South%20Africa/?current_page={i}"
        r = session.get(api, headers=headers)
        js = r.json()["data"]

        for j in js:
            store_number = j.get("storelocator_id")
            if not store_number:
                continue

            raw_address = ", ".join(j.get("address") or [])
            street_address = get_international(raw_address, s=True)
            city = j.get("city") or get_international(raw_address, c=True)
            postal = j.get("zipcode") or get_international(raw_address, p=True)
            country_code = j.get("country_id")
            location_name = j.get("storename")
            page_url = f"https://www.paul-bakeries.com/en/bakeries/index/view/id/{store_number}/"
            phone = j.get("telephone") or ""
            if phone.count("0") == 10:
                phone = SgRecord.MISSING
            latitude = j.get("latitude") or ""
            longitude = j.get("longitude")
            if "." not in latitude:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            _tmp = []
            source = j.get("storetime") or "[]"
            hours = json.loads(source)
            for h in hours:
                day = h.get("days")
                if not h.get("day_status"):
                    _tmp.append(f"{day}: Closed")

                open_hour = h.get("open_hour")
                open_minute = h.get("open_minute")
                close_hour = h.get("close_hour")
                close_minute = h.get("close_minute")
                _tmp.append(
                    f"{day}: {open_hour}:{open_minute}-{close_hour}:{close_minute}"
                )

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                raw_address=raw_address,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)

        pages = r.json().get("totalPages") or 0
        if i >= pages:
            break


if __name__ == "__main__":
    locator_domain = "https://www.lincare.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
