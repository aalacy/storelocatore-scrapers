from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.pause_resume import CrawlStateSingleton
from concurrent import futures


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        days = h.get("day")
        opens = h.get("openingHour")
        closes = h.get("closingHour")
        line = f"{days} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def get_data(zipp, sgw: SgWriter):

    locator_domain = "https://www.bigotires.com"
    api_url = "https://www.bigotires.com/restApi/dp/v1/store/storesByAddress"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json;charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "X-Requested-By": "123",
        "Origin": "https://www.bigotires.com",
        "Connection": "keep-alive",
        "Referer": "https://www.bigotires.com/store-locator",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    data = '{"address":"' + zipp + '"}'
    session = SgRequests()

    r = session.post(api_url, headers=headers, data=data)
    try:
        js = r.json()["storesType"]["stores"]
    except:
        js = []
        return
    for j in js:
        a = j.get("address")
        page_url = f"https://www.bigotires.com{j.get('storeDetailsUrl')}"

        location_name = "<MISSING>"
        street_address = a.get("address1") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zipcode") or "<MISSING>"
        store_number = j.get("storeNumber")
        country_code = "US"
        phone = (
            "".join(a.get("phoneNumber").get("areaCode"))
            + " "
            + "".join(a.get("phoneNumber").get("firstThree"))
            + " "
            + "".join(a.get("phoneNumber").get("lastFour"))
        )
        latitude = j.get("mapCenter").get("latitude") or "<MISSING>"
        longitude = j.get("mapCenter").get("latitude") or "<MISSING>"
        hours = j.get("workingHours")
        hours_of_operation = get_hours(hours)

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


def fetch_data(sgw: SgWriter):
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=1,
        expected_search_radius_miles=1,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
