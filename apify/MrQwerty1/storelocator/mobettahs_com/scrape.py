from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://mobettahs.com/modules/multilocation/?near_location=75022&threshold=4000&distance_unit=miles&limit=200&services__in=&language_code=en-us&published=1&within_business=true"
    r = session.get(api, headers=headers)
    js = r.json()["objects"]

    for j in js:
        adr1 = j.get("street") or ""
        adr2 = j.get("street2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "US"
        store_number = j.get("id")
        location_name = j.get("location_name")
        page_url = j.get("location_url")
        phone = j["phonemap"]["phone"]
        latitude = j.get("lat")
        longitude = j.get("lon")

        try:
            hours = j["formatted_hours"]["primary"]["grouped_days"]
        except:
            hours = []

        _tmp = []
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://mobettahs.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
