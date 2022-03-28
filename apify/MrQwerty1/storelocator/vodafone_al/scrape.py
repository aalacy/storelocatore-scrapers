from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.vodafone.al/service/?type=getStores"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        slug = j.get("path") or ""
        page_url = f"https://www.vodafone.al{slug}"
        phone = j.get("telephone")
        street_address = j.get("address_name")
        city = j.get("city")
        state = j.get("area")
        postal = j.get("postal_code")

        _tmp = []
        hours = j.get("workingHours") or []
        for h in hours:
            day = h.get("day")
            inter = h.get("hours")
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="AL",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.al/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
