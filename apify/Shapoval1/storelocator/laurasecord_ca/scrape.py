from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        days = h.get("weekday")
        opens = h.get("start")
        closes = h.get("stop")
        line = f"{days} - {opens} - {closes}"
        if opens == closes:
            line = f"{days} Closed"
        tmp.append(line)
    hours_of_operation = ";".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://laurasecord.ca"
    api_url = "https://store.laurasecord.ca/api/store/forsite"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()["data"]

    for j in js:

        location_name = j.get("name")
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("province")
        country_code = "CA"
        postal = j.get("postal_code")
        store_number = j.get("store_id")
        page_url = "https://laurasecord.ca/find-a-store/"
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")

        session = SgRequests()
        r = session.get(
            f"https://store.laurasecord.ca/api/store/forsite/{store_number}/hours",
            headers=headers,
        )
        js = r.json()
        hours = js.get("data")

        hours_of_operation = get_hours(hours)
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
