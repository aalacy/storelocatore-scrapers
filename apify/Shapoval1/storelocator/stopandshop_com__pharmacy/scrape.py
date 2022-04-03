from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://stopandshop.com/pharmacy"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "X-ContactId": "",
        "X-SessionId": "",
        "X-ProductionLevel": "0",
        "Origin": "https://stopandshopweb.rxtouch.com",
        "Connection": "keep-alive",
        "Referer": "https://stopandshopweb.rxtouch.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    }

    session = SgRequests()

    data = '{"vcZIPCode":"' + zips + '","vcLocale":"en-US"}'

    r = session.post(
        "https://api-cs.rxtouch.com/rxwebapi/1.0.8/stopandshop/api/Store/GetStoresByZip",
        headers=headers,
        data=data,
    )
    try:
        js = r.json()["data"] or []
    except:
        return
    if not js:
        return

    for j in js:

        page_url = "https://stopandshop.com/pharmacy"
        location_name = "".join(j.get("nvcStoreName"))
        street_address = f"{j.get('nvcAddress1')} {j.get('nvcAddress2')}".strip()
        city = j.get("nvcCity")
        state = j.get("nvcState")
        postal = j.get("vcZip")
        country_code = "US"
        phone = j.get("vcPharmacyPhone") or "<MISSING>"
        latitude = j.get("fLatitude")
        longitude = j.get("fLongitude")
        hours_of_operation = (
            "".join(j.get("Details")[0].get("nvcDescription"))
            .replace("\r", " ")
            .replace("\n", " ")
            .strip()
        )
        try:
            store_number = location_name.split("#")[1].strip()
        except:
            store_number = "<MISSING>"

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=20,
        expected_search_radius_miles=20,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
