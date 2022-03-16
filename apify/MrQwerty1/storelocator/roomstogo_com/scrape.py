from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_name(api):
    r = session.get(api, headers=headers)
    return r.json()["result"]["data"]["strapiStore"]["SEO"]["SEO"]["PageTitle"]


def fetch_data(sgw: SgWriter):
    api = "https://www.roomstogo.com/page-data/stores/page-data.json"
    r = session.get(api, headers=headers)
    js = r.json()["result"]["pageContext"]["stores"]["stores"]

    for j in js:
        slug = j.get("slug")
        app = f"https://www.roomstogo.com/page-data{slug}/page-data.json"
        location_name = get_name(app) or ""
        if " - We" in location_name:
            location_name = location_name.split("- We")[0]
        page_url = f"https://www.roomstogo.com{slug}"
        city = j.get("City")
        state = j.get("State")
        postal = j.get("Zip")
        adr1 = j.get("Address1") or ""
        if f", {city}," in adr1:
            adr1 = adr1.split(f", {city}")[0].strip()
        adr2 = j.get("Address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        phone = j.get("PhoneNumber")
        try:
            loc = j["Location"]["latLng"]
        except:
            loc = dict()
        latitude = loc.get("lat")
        longitude = loc.get("lng")
        location_type = j.get("StoreType")
        store_number = j.get("StoreNumber")

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hours = j.get("StoreHours") or {}
        for d in days:
            start = hours.get(f"{d}Open")
            if not start:
                _tmp.append(f"{d}: Closed")
                continue
            end = hours.get(f"{d}Closed")
            _tmp.append(f"{d}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.roomstogo.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
