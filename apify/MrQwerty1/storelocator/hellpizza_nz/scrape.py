from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://api.hellpizza.com/1.0/regions/region-info.json"
    r = session.get(api, headers=headers)
    states = r.json()["payload"]

    for s in states:
        state = s.get("name")
        state_slug = s.get("key")
        js = s.get("stores") or []

        for j in js:
            location_name = j.get("name") or ""
            raw_address = j.get("location") or ""
            street_address = raw_address.split(", ")[0]
            city = location_name
            postal = raw_address.split()[-1]
            country_code = "NZ"
            store_number = j.get("store_id")
            page_url = (
                f"https://hellpizza.nz/find_store/{state_slug}/{location_name.lower()}"
            )
            phone = j.get("phone_number")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            _tmp = []
            hours = j.get("open_days") or []
            for h in hours:
                day = h.get("day")
                start = h.get("open")
                end = h.get("close")
                _tmp.append(f"{day}: {start}-{end}")

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
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://hellpizza.nz/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
