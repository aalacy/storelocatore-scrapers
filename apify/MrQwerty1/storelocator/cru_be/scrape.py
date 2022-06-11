from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://cru.be/api/v2/establishments"
    r = session.get(api, headers=headers)
    js = r.json()["establishments"]

    for j in js:
        a = j.get("address") or {}
        adr1 = a.get("street_and_number") or ""
        adr2 = a.get("address_extra") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        postal = a.get("postal_code")
        country_code = "BE"
        store_number = j.get("id")
        location_name = j.get("name")
        page_url = f"https://cru.be/nl/markets?establishment={store_number}#"
        phone = j.get("phone")
        latitude = a.get("latitude")
        longitude = a.get("longitude")

        _tmp = []
        hours = j.get("opening_hours") or []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for h in hours:
            index = int(h.get("day")) - 1
            day = days[index]
            start = h.get("opening_hour")
            end = h.get("closing_hour")
            _tmp.append(f"{day}: {start}-{end}")

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://cru.be/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
