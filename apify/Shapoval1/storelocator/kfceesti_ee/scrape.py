from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kfc.lt"
    api_url = "https://production.ee.kfc.digital/api/store/v2/store.geo_search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Origin": "https://kfceesti.ee",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Referer": "https://kfceesti.ee/",
        "Connection": "keep-alive",
        "TE": "trailers",
    }

    data = '{"coordinates":[59.42239999999998,24.79387],"radiusMeters":100000,"channel":"website"}'

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["searchResults"]
    for j in js:
        a = j.get("store")
        page_url = "https://kfceesti.ee/restaurants"
        location_name = a.get("title").get("en")
        street_address = a.get("contacts").get("streetAddress").get("en")
        country_code = "Estonia"
        city = a.get("contacts").get("city").get("en")
        store_number = a.get("storeId")
        latitude = (
            a.get("contacts").get("coordinates").get("geometry").get("coordinates")[0]
        )
        longitude = (
            a.get("contacts").get("coordinates").get("geometry").get("coordinates")[1]
        )
        phone = a.get("contacts").get("phoneNumber")
        hours_of_operation = (
            a.get("openingHours").get("regular").get("startTimeLocal")
            + " - "
            + a.get("openingHours").get("regular").get("endTimeLocal")
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
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
