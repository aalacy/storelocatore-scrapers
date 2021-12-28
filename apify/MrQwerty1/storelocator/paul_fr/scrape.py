import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(500):
        api = f"https://www.paul.fr/default/storelocator/index/ajax/?current_page={i}"
        r = session.get(api, headers=headers)
        js = r.json()["data"]

        for j in js:
            location_name = j.get("storename")
            page_url = j.get("store_url")
            ad = j.get("address") or []
            street_address = ", ".join(ad)
            city = j.get("city")
            state = j.get("region_id")
            postal = j.get("zipcode")
            country = j.get("country_id")

            phone = j.get("telephone") or ""
            if str(phone).count("0") > 5:
                phone = SgRecord.MISSING
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            store_number = j.get("storelocator_id")
            status = j.get("status") or ""
            if status == "closed" or country != "FR":
                continue

            _tmp = []
            text = j.get("storetime") or ""
            if text:
                hours = json.loads(text)
            else:
                hours = []

            for h in hours:
                day = h.get("days")
                start_hour = h.get("open_hour")
                start_min = h.get("open_minute")
                end_hour = h.get("close_hour")
                end_min = h.get("close_minute")
                _tmp.append(f"{day}: {start_hour}:{start_min}-{end_hour}:{end_min}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                location_name=location_name,
                page_url=page_url,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 5:
            break


if __name__ == "__main__":
    locator_domain = "https://www.paul.fr/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
