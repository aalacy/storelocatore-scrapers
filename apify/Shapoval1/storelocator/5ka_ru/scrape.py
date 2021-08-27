import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://5ka.ru"
    api_url = "https://5ka.ru/api/v2/stores/?bbox=55.72707248109838,37.46492785595701,55.77934992845011,37.78009814404297"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    jsblock = r.text.split("callback(")[1].split(");")[0].strip()
    js = json.loads(jsblock)
    for j in js["data"]["features"]:
        a = j.get("properties")
        page_url = "https://5ka.ru/stores/"
        location_name = "<MISSING>"
        location_type = a.get("type")
        street_address = "".join(a.get("address")).replace(",", "").strip()
        country_code = "RU"
        city = "".join(a.get("city_name")) or "г.Москва"
        if street_address.find(f"{city}") != -1:
            street_address = street_address.replace(f"{city}", "").strip()
        latitude = j.get("geometry").get("coordinates")[0]
        longitude = j.get("geometry").get("coordinates")[1]
        phone = a.get("phone")
        hours_of_operation = f"{a.get('work_start_time')} - {a.get('work_end_time')}"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
