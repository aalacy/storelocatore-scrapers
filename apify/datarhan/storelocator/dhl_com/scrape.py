import demjson

from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton


@retry(stop=stop_after_attempt(3))
def fetch_latlng(lat, lng, country, session, tracker):
    url = "https://wsbexpress.dhl.com/ServicePointLocator/restV3/servicepoints"
    params = {
        "servicePointResults": 50,
        "countryCode": country,
        "latitude": lat,
        "longitude": lng,
        "language": "eng",
        "key": "963d867f-48b8-4f36-823d-88f311d9f6ef",
    }
    response = session.get(url, params=params)
    if response.status_code != 200:
        return []
    data = demjson.decode(response.text)
    if not data.get("servicePoints"):
        return []

    for location in data.get("servicePoints"):
        poi = extract(location)
        yield poi


def extract(poi):
    domain = "dhl.com"
    location_name = poi["servicePointName"]
    location_name = location_name if location_name else "<MISSING>"
    street_address = poi["address"]["addressLine1"]
    if poi["address"]["addressLine2"]:
        street_address += ", " + poi["address"]["addressLine2"]
    if poi["address"]["addressLine3"]:
        street_address += ", " + poi["address"]["addressLine3"]
    street_address = street_address if street_address else "<MISSING>"
    city = poi["address"]["city"]
    city = city if city else "<MISSING>"
    state = poi["address"]["state"]
    state = state if state else "<MISSING>"
    zip_code = poi["address"]["zipCode"]
    zip_code = zip_code if zip_code else "<MISSING>"
    country_code = poi["address"]["country"]
    country_code = country_code if country_code else "<MISSING>"
    store_number = poi["facilityId"]
    store_number = store_number if store_number else "<MISSING>"
    phone = poi["contactDetails"].get("phoneNumber")
    phone = phone if phone else "<MISSING>"
    location_type = poi["servicePointType"]
    location_type = location_type if location_type else "<MISSING>"
    latitude = poi["geoLocation"]["latitude"]
    longitude = poi["geoLocation"]["longitude"]
    latitude = latitude if latitude else "<MISSING>"
    longitude = longitude if longitude else "<MISSING>"
    hours_of_operation = []
    for elem in poi["openingHours"]["openingHours"]:
        day = elem["dayOfWeek"]
        opens = elem["openingTime"]
        closes = elem["closingTime"]
        hours_of_operation.append("{} {} - {}".format(day, opens, closes))
    hours_of_operation = (
        ", ".join(hours_of_operation).split(", HOLIDAY")[0]
        if hours_of_operation
        else "<MISSING>"
    )

    item = SgRecord(
        locator_domain=domain,
        page_url=SgRecord.MISSING,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_code,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    return item


def fetch_data():
    tracker = []

    session = SgRequests()
    session.get("https://locator.dhl.com/ServicePointLocator/restV3/appConfig")

    with ThreadPoolExecutor() as executor:
        futures = []
        futures.extend(
            executor.submit(fetch_latlng, lat, lng, "US", session, tracker)
            for lat, lng in static_coordinate_list(5, SearchableCountries.USA)
        )
        futures.extend(
            executor.submit(fetch_latlng, lat, lng, "CA", session, tracker)
            for lat, lng in static_coordinate_list(10, SearchableCountries.CANADA)
        )

        for future in as_completed(futures):
            locations = future.result()
            for loc in locations:
                yield loc


def scrape():
    CrawlStateSingleton.get_instance().save(override=True)
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
