from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(1, 20):
        api = f"https://chickene.com/wp-json/wp/v2/store_location?per_page=100&page={i}"
        r = session.get(api, headers=headers)
        js = r.json()

        for j in js:
            location_name = j["title"]["rendered"]
            location_name = location_name.replace("&#8211;", "–")
            store_number = j["id"]
            acf = j.get("acf") or {}

            phone = acf.get("phone_number")
            a = acf.get("address") or {}
            raw_address = a.get("address") or ""
            if ", USA" in raw_address:
                raw_address = raw_address.replace(", USA", "")
            line = raw_address.split(",")
            state = line.pop().strip()
            city = line.pop().strip()
            street_address = ",".join(line)
            postal = a.get("post_code") or ""
            if postal.isalpha():
                postal = SgRecord.MISSING

            latitude = a.get("lat")
            longitude = a.get("lng")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)

        if len(js) < 100:
            break


if __name__ == "__main__":
    locator_domain = "https://chickene.com/"
    page_url = "https://chickene.com/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
