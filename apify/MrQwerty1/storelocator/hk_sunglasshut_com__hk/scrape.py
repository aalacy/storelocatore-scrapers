from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://hk.sunglasshut.com/api/content/render/false/limit/9999/type/json/query/+contentType:SghStoreLocator%20+languageId:8%20+deleted:false%20+working:true/orderby/modDate%20desc"

    r = session.get(api)
    js = r.json()["contentlets"]

    for j in js:
        location_name = j.get("name")
        slug = j.get("URL_MAP_FOR_CONTENT")
        page_url = f"https://hk.sunglasshut.com/hk{slug}".replace("-details", "")
        street_address = j.get("address")
        city = j.get("city")
        postal = j.get("zip")
        phone = j.get("phone")
        latitude = j.get("geographicCoordinatesLatitude")
        longitude = j.get("geographicCoordinatesLongitude")
        if latitude == 0:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

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
        for day in days:
            _tmp.append(f"{day}: {j.get(day)}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            location_name=location_name,
            page_url=page_url,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="HK",
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://sea.sunglasshut.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
