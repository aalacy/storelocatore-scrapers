from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return SgRecord.MISSING
    return field


def format_hours(hours_json):
    if not hours_json or not len(hours_json) == 7:
        return SgRecord.MISSING
    DAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    parts = []
    for day in hours_json:
        text = ""
        text += DAYS[day["day"]] + ": "
        text += day["start_time"]
        text += "-"
        text += day["end_time"]
        parts.append(text)
    return ", ".join(parts)


def fetch_data(sgw: SgWriter):
    page = 1
    while True:
        response = session.get(URL_TEMPLATE.format(page), headers=HEADERS).json()
        page += 1
        stores = response["results"]
        if not stores:
            break
        for store in stores:
            street_address = handle_missing(store["contact"]["address1"])
            city = handle_missing(store["contact"]["city"])
            zip_code = handle_missing(store["contact"]["post_code"])
            store_number = store["code"]
            phone = handle_missing(store["contact"]["telephone"])
            location_type = handle_missing(store["store_type"])
            latitude = handle_missing(store["location"]["lat"])
            longitude = handle_missing(store["location"]["lon"])
            hours_of_operation = format_hours(store["opening_times"])

            if location_type == "main":
                location_name = "Sainsbury’s Superstore"
            else:
                location_name = "Sainsbury’s Local"

            row = SgRecord(
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip_code,
                country_code="GB",
                store_number=store_number,
                location_type=location_type,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://sainsburys.co.uk/"
    URL_TEMPLATE = "https://stores.sainsburys.co.uk/api/v1/stores/?fields=slfe-list-2.21&api_client_id=slfe&lat=53.3901702&lon=-1.51136&limit=50&store_type=main%2Clocal&sort=by_distance&within=10000&page={}"
    HEADERS = {
        "Authority": "stores.sainsburys.co.uk",
        "Referer": "https://stores.sainsburys.co.uk/list/place/@53.3901702,-12.7924904,/1/all",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
