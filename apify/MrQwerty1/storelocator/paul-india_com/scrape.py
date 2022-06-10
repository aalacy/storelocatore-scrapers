from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.paul-india.com/wp-admin/admin-ajax.php?action=store_search&lat=28.68627&lng=77.22178&max_results=100&search_radius=5000"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("store") or ""
        location_name = location_name.replace("&#8211;", "-")
        street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")

        phone = j.get("phone") or ""
        if "/" in phone:
            phone = phone.split("/")[0].strip()

        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="IN",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.paul-india.com/"
    page_url = "https://www.paul-india.com/store-locator/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
