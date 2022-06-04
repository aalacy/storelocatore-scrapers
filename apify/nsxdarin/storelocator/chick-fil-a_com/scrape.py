from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://www.chick-fil-a.com/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://locator.chick-fil-a.com.yext-cdn.com/search?q=10001&per=10",
        "Alt-Used": "locator.chick-fil-a.com.yext-cdn.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = {
        "q": f"{zips}",
        "per": "50",
        "r": "250",
    }

    r = session.get(
        "https://locator.chick-fil-a.com.yext-cdn.com/search",
        headers=headers,
        params=params,
    )
    try:
        js = r.json()["response"]["entities"]
    except:
        return

    for j in js:

        a = j.get("profile")
        page_url = a.get("websiteUrl")
        location_name = a.get("c_locationName") or "<MISSING>"
        street_address = a.get("address").get("line1") or "<MISSING>"
        city = a.get("address").get("city") or "<MISSING>"
        state = a.get("address").get("region") or "<MISSING>"
        postal = a.get("address").get("postalCode") or "<MISSING>"
        if str(street_address).find("4531 Weitzel St Timnath CO80547") != -1:
            street_address = str(street_address).split(f"{city}")[0].strip()
        country_code = a.get("address").get("countryCode")
        if country_code == "CA":
            page_url = "https://www.chick-fil-a.com/locations"
        try:
            phone = a.get("mainPhone").get("display")
        except:
            phone = "<MISSING>"
        latitude = a.get("displayCoordinate").get("lat") or "<MISSING>"
        longitude = a.get("displayCoordinate").get("long") or "<MISSING>"
        days = a.get("hours", {}).get("normalHours") or []

        _tmp = []
        for d in days:
            day = d.get("day")[:3].capitalize()
            try:
                interval = d.get("intervals")[0]
                start = str(interval.get("start"))
                end = str(interval.get("end"))

                if len(start) == 3:
                    start = f"0{start}"

                if len(end) == 3:
                    end = f"0{end}"

                line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
            except IndexError:
                line = f"{day}  Closed"

            _tmp.append(line)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if (
            hours_of_operation.count("Closed") == 7
            or location_name.lower().find("closed") != -1
        ):
            hours_of_operation = "Closed"
        store_number = a.get("meta").get("id") or "<MISSING>"
        status = a.get("c_status")
        if status == "FUTURE":
            hours_of_operation = "Coming Soon"
        if status == "TEMPORARY_CLOSE" and location_name != "Northpark Mall (IA)":
            hours_of_operation = "TEMPORARY CLOSE"

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
        max_search_distance_miles=70,
        expected_search_radius_miles=70,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
