from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.pause_resume import CrawlStateSingleton
from concurrent import futures


def get_hours(hours) -> str:
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    tmp = []
    for d in days:
        day = d
        try:
            closed = hours.get(d).get("isClosed")
        except:
            closed = True
        if not closed:
            start = hours.get(d).get("openIntervals")[0].get("start")
            close = hours.get(d).get("openIntervals")[0].get("end")
            line = f"{day} {start} - {close}"
            tmp.append(line)
        if closed:
            line = f"{day} - Closed"
            tmp.append(line)
    hours_of_operation = ";".join(tmp) or "<MISSING>"
    return hours_of_operation


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://www.pitapitusa.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    session = SgRequests()
    r = session.get(
        f"https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=50&location={str(zips)}&limit=50&api_key=0044bc2f8e2fa0fe5019f2301f8cdd49&v=20181201&resolvePlaceholders=true&entityTypes=location",
        headers=headers,
    )
    js = r.json()
    for j in js["response"]["entities"]:
        a = j.get("address")
        page_url = (
            j.get("c_baseURL") or f"https://locations.pitapitusa.com/?q={str(zips)}"
        )
        if page_url.find("https://pitapit.ca/") != -1:
            continue
        if page_url.find("zip") != -1:
            page_url = j.get("c_baseURL")
        location_name = j.get("name") or "<MISSING>"
        street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("region") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("countryCode") or "<MISSING>"
        phone = j.get("mainPhone") or "<MISSING>"
        latitude = j.get("yextDisplayCoordinate").get("latitude")
        longitude = j.get("yextDisplayCoordinate").get("longitude")
        location_type = "location"
        hours = j.get("hours")
        hours_of_operation = get_hours(hours)
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=30,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=7) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
