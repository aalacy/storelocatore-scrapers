from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.benchmarkseniorliving.com/wp-json/communities/v1/json"
    r = session.get(api, headers=headers)
    js = r.json()["entities"]

    for j in js:
        a = j.get("address") or {}
        adr1 = a.get("addressLine1") or ""
        adr2 = a.get("addressLine2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("locality")
        state = a.get("administrativeArea")
        postal = a.get("postalCode")
        country_code = "US"
        store_number = j.get("id")
        location_name = j.get("title") or ""
        location_name = location_name.replace("&#8217;", "'")
        if "Test" in location_name:
            continue
        page_url = j["url"]["path"]
        phone = j.get("phone")

        p = j.get("position") or {}
        latitude = p.get("lat")
        longitude = p.get("lng")

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.benchmarkseniorliving.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
