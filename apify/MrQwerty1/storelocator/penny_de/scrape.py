from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.penny.de/.rest/market"
    r = session.get(api, headers=headers)
    js = r.json()["results"]

    for j in js:
        location_name = j.get("marketName")
        adr1 = j.get("street") or ""
        adr2 = j.get("streetNumber") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        postal = j.get("zipCode")
        country_code = "DE"
        store_number = j.get("wwIdent")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days:
            start = j.get(f"opensAt{day}")
            end = j.get(f"closesAt{day}")
            if not start:
                continue
            if start == end:
                _tmp.append(f"{day}: Closed")
                continue
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
    locator_domain = "https://www.penny.de/"
    page_url = "https://www.penny.de/marktsuche"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
