from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
import json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("costa_co_uk")
DOMAIN = "costa.co.uk"
MISSING = SgRecord.MISSING
MAX_WORKERS = 10


headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(50))
def get_response(url):
    with SgRequests(verify_ssl=False, timeout_config=400) as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} <<= {response.status_code} OK!==>")  # noqa
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def fetch_records(latlng, sgw):
    total = 0
    lat, lng = latlng
    url = f"https://www.costa.co.uk/api/locations/stores?latitude={str(lat)}&longitude={str(lng)}&maxrec=500"
    try:
        r = get_response(url)
        js = json.loads(r.content)["stores"]
        logger.info(f"Pulling the data from : {r.url} ")
        if js:
            total += len(js)
            for item in js:
                locator_domain = DOMAIN
                store_number = item["storeNo8Digit"]
                location_type = item["storeType"]

                # Phone
                phone = item["telephone"]
                if phone == "":
                    phone = MISSING

                # Street Address
                add1 = item["storeAddress"]["addressLine1"]
                add = (
                    add1
                    + " "
                    + item["storeAddress"]["addressLine2"]
                    + " "
                    + item["storeAddress"]["addressLine3"]
                )
                add = add.strip()
                street_address = ""
                if add == "" or add is None:
                    street_address = MISSING
                else:
                    street_address = add

                # Location Name
                location_name = item["storeNameExternal"]
                if location_name == "":
                    location_name = location_type

                # City Name
                city = item["storeAddress"]["city"]
                if city == "":
                    city = item["storeAddress"]["addressLine3"]
                if city == "" or city is None:
                    city = MISSING
                if city == MISSING:
                    city = location_name
                if "Belfast" in location_name:
                    city = "Belfast"
                if "Knightswick" in location_name:
                    city = "Knightswick"
                if "Lewes" in location_name:
                    city = "Lewes"
                if "Belper" in location_name:
                    city = "Belper"
                if "Barrow in Furness" in location_name:
                    city = "Barrow in Furness"
                if "Washington" in location_name:
                    city = "Washington"
                if "Purfleet" in add:
                    city = "Purfleet"
                if "Taunton" in location_name:
                    city = "Taunton"
                if "Hempstead Valley" in location_name:
                    city = "Hempstead Valley"
                if "Belfast" in add:
                    city = "Belfast"
                if "Bideford" in location_name:
                    city = "Bideford"

                # State
                state = MISSING

                # Zip Postal
                zip_postal = item["storeAddress"]["postCode"]
                if zip_postal == "" or zip_postal is None:
                    zip_postal = MISSING

                # Country Code
                country_code = "GB"

                # Latitude and Longitude
                latitude = item["latitude"]
                latitude = latitude if latitude else MISSING

                longitude = item["longitude"]
                longitude = longitude if longitude else MISSING

                # page url
                page_url = ""
                if MISSING not in latitude or MISSING not in longitude:
                    page_url = f"https://www.costa.co.uk/locations/store-locator/map?latitude={latitude}&longitude={longitude}"
                else:
                    page_url = "https://www.costa.co.uk/locations/store-locator"

                # Hours of Operation
                soh = item["storeOperatingHours"]
                mon = "Mon: " + soh["openMon"] + "-" + soh["closeMon"]
                tue = "Tue: " + soh["openTue"] + "-" + soh["closeTue"]
                wed = "Wed: " + soh["openWed"] + "-" + soh["closeWed"]
                thu = "Thu: " + soh["openThu"] + "-" + soh["closeThu"]
                fri = "Fri: " + soh["openFri"] + "-" + soh["closeFri"]
                sat = "Sat: " + soh["openSat"] + "-" + soh["closeSat"]
                sun = "Sun: " + soh["openSun"] + "-" + soh["closeSun"]
                hours_of_operation = f"{mon}; {tue}; {wed}; {thu}; {fri}; {sat}; {sun}"
                if ":" not in hours_of_operation:
                    hours_of_operation = MISSING

                if (
                    "Mon: -; Tue: -; Wed: -; Thu: -; Fri: -; Sat: -; Sun: -"
                    in hours_of_operation
                ):
                    hours_of_operation = MISSING

                # Clean street_address
                if street_address is not None or street_address:
                    street_address = " ".join(street_address.split())

                raw_address = MISSING
                item = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
                sgw.write_row(item)
            logger.info(
                f'Number of items found: {len(json.loads(r.content)["stores"])} : Total: {total}'
            )
        else:
            return

    except Exception as e:
        logger.info(f"Please fix FetchRecordsError: << {e} >> << {url} >> ")  # noqa


def fetch_data(sgw: SgWriter):
    logger.info("Started")
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        expected_search_radius_miles=5,
        granularity=Grain_8(),
        use_state=False,
    )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_global = [executor.submit(fetch_records, latlng, sgw) for latlng in search]
        tasks.extend(task_global)
        for future in as_completed(tasks):
            future.result()


def scrape():

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
