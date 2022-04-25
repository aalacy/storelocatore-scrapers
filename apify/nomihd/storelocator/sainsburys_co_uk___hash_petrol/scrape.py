from sgscrape.sgrecord import SgRecord
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


log = sglog.SgLogSetup().get_logger(logger_name="sainsburys.co.uk")


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
            store_number = store["code"]
            log.info(f"fetching data for store having ID: {store_number}")
            substores = session.get(
                f"https://stores.sainsburys.co.uk/api/v1/stores/{store_number}/?fields=slfe-details-2.21&api_client_id=slfe",
                headers=HEADERS,
            ).json()["store"]["substores"]
            for sub in substores:
                if sub["store_type"] == "pfs":
                    street_address = handle_missing(sub["contact"]["address1"])
                    city = handle_missing(sub["contact"]["city"])
                    zip_code = handle_missing(sub["contact"]["post_code"])
                    phone = handle_missing(sub["contact"]["telephone"])
                    location_type = handle_missing(sub["store_type"])
                    latitude = handle_missing(sub["location"]["lat"])
                    longitude = handle_missing(sub["location"]["lon"])
                    hours_of_operation = format_hours(sub["opening_times"])
                    location_name = handle_missing(sub["other_name"])
                    slug = store["other_name"].replace(" ", "-").strip().lower()
                    page_url = f"https://stores.sainsburys.co.uk/{store_number}/{slug}"
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
                        page_url=page_url,
                    )

                    sgw.write_row(row)
                    break


if __name__ == "__main__":
    locator_domain = "https://sainsburys.co.uk/#petrol"
    URL_TEMPLATE = "https://stores.sainsburys.co.uk/api/v1/stores/?fields=slfe-list-2.21&api_client_id=slfe&lat=53.3901702&lon=-1.51136&limit=50&store_type=main%2Clocal&sort=by_distance&within=10000&facility=Petrol&page={}"
    HEADERS = {
        "Authority": "stores.sainsburys.co.uk",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
