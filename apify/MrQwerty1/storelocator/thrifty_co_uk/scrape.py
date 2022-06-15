from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(0, 10000, 1000):
        api = f"https://www.thrifty.com/loc/modules/multilocation/?near_location=Sydney&threshold=50000&distance_unit=miles&limit=1000&language_code=en-us&published=1&within_business=true&offset={i}"
        r = session.get(api, headers=headers)
        js = r.json()["objects"]

        for j in js:
            adr1 = j.get("street") or ""
            adr2 = j.get("street2") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = j.get("city") or ""
            if "(" in city:
                city = city.split("(")[0].strip()
            state = j.get("state")
            postal = j.get("postal_code") or ""
            if str(postal) == "0":
                postal = SgRecord.MISSING
            country_code = j.get("country")
            store_number = j.get("id")
            location_name = j.get("location_name")
            try:
                phone = j["phones"][0]["e164"]
            except:
                phone = SgRecord.MISSING
            latitude = j.get("lat")
            longitude = j.get("lon")
            raw_address = j.get("formatted_address")

            _tmp = []
            try:
                hours = j["formatted_hours"]["primary"]["grouped_days"]
            except KeyError:
                hours = []

            for h in hours:
                day = h.get("label_abbr")
                inter = h.get("content")
                _tmp.append(f"{day}: {inter}")

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
                raw_address=raw_address,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)

        if len(js) < 1000:
            break


if __name__ == "__main__":
    locator_domain = "https://www.thrifty.com/"
    page_url = "https://www.thrifty.com/loc/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
