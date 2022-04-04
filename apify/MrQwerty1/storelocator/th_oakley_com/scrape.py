from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    ccs = ["th", "tw", "sg", "my", "id", "hk"]
    for cc in ccs:
        locator_domain = f"https://{cc}.oakley.com/"
        page_url = f"https://{cc}.oakley.com/en/store-finder"
        api = f"https://{cc}.oakley.com/assets/json/{cc}-stores.json"
        r = session.get(api, headers=headers)
        js = r.json()

        for j in js:
            street_address = j.get("address")
            city = j.get("city")
            state = j.get("state")
            postal = j.get("postal")
            country_code = cc.upper()
            store_number = j.get("customer_number")
            location_name = j.get("name")
            phone = j.get("phone") or ""
            phone = phone.replace("Sementara", "").strip()
            if "/" in phone:
                phone = phone.split("/")[0].strip()
            if "E" in phone:
                phone = phone.split("E")[0].strip()

            latitude = j.get("lat")
            longitude = j.get("lng")

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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
