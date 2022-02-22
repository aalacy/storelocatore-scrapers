from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://ordering.zyda.com/jollibeekw/branches"
    r = session.get(api)

    for j in r.json()["data"]:
        store_number = j.get("id")
        page_url = f"https://www.jollibeekw.com/branches/{store_number}"
        location_type = j.get("types")
        j = j.get("attributes")
        location_name = j.get("title-en")
        street_address = j.get("address-en")
        phone = j.get("contact-number")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("opening-hours") or []
        for h in hours:
            day = h.get("day")
            start = h.get("open-at")
            end = h.get("close-at")
            _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            country_code="KW",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.jollibeekw.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
