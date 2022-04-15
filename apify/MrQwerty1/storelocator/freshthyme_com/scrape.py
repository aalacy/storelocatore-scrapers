from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api_url = "https://discover.freshthyme.com/api/v2/stores"

    r = session.get(api_url)
    js = r.json()["items"]

    for j in js:
        a = j.get("address")
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        city = a.get("city")
        state = a.get("province")
        postal = a.get("postal_code")
        country_code = "US"
        store_number = j.get("ext_id")
        page_url = f"https://www.freshthyme.com/stores/{store_number}"
        location_name = j.get("name")
        phone = j.get("phone_number")
        loc = j.get("location")
        latitude = loc.get("latitude")
        longitude = loc.get("longitude")

        _tmp = []
        hours = j.get("store_hours") or {}
        for k, v in hours.items():
            start = v.get("start")
            end = v.get("end")
            if start:
                _tmp.append(f"{k.capitalize()}: {start[:-3]} - {end[:-3]}")
            else:
                _tmp.append(f"{k.capitalize()}: Closed")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.freshthyme.com/"

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
