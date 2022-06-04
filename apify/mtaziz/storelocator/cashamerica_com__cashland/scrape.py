from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("cashamerica_com__cashland")
MISSING = SgRecord.MISSING
MAX_WORKERS = 10

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(60))
def get_response(urlnum, url):
    with SgRequests(timeout_config=600) as http:
        logger.info(f"[{urlnum}] Pulling the data from: {url}")
        r = http.get(url, headers=headers)
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        elif r.status_code == 500:
            return
        else:
            raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def fetch_records(key, idx, url_data, sgw: SgWriter):
    try:
        r = get_response(idx, url_data)
        if r is None:
            return
        else:
            try:
                data = r.json()
            except AttributeError as e:
                logger.info(f"Fix AttributeError {e}")
                return
            logger.info(f"[ Pulling the data from] {url_data}")
            for i in range(len(data)):
                store_data = data[i]
                # Locator Domain
                locator_domain = "https://cashamerica.com/cashland"

                # Page URL
                page_url = "<INACCESSIBLE>"

                # Location Name
                location_name = store_data["brand"] if store_data["brand"] else MISSING

                # Street Address
                street_address = ""
                if store_data["address"]["address2"] is not None:
                    street_address = (
                        store_data["address"]["address1"]
                        + store_data["address"]["address2"]
                    )
                else:
                    street_address = store_data["address"]["address1"]

                # City
                city = (
                    store_data["address"]["city"]
                    if store_data["address"]["city"]
                    else MISSING
                )

                # State
                state = ""
                if store_data["address"]["state"] in [
                    "AL",
                    "AK",
                    "AZ",
                    "AR",
                    "CA",
                    "CO",
                    "CT",
                    "DC",
                    "DE",
                    "FL",
                    "GA",
                    "HI",
                    "ID",
                    "IL",
                    "IN",
                    "IA",
                    "KS",
                    "KY",
                    "LA",
                    "ME",
                    "MD",
                    "MA",
                    "MI",
                    "MN",
                    "MS",
                    "MO",
                    "MT",
                    "NE",
                    "NV",
                    "NH",
                    "NJ",
                    "NM",
                    "NY",
                    "NC",
                    "ND",
                    "OH",
                    "OK",
                    "OR",
                    "PA",
                    "RI",
                    "SC",
                    "SD",
                    "TN",
                    "TX",
                    "UT",
                    "VT",
                    "VA",
                    "WA",
                    "WV",
                    "WI",
                    "WY",
                ]:
                    state = store_data["address"]["state"]
                state = state if state else MISSING

                # Zip Code
                zipcode = store_data["address"]["zipCode"]
                if "00000" in store_data["address"]["zipCode"]:
                    zipcode = MISSING
                zipcode = zipcode if zipcode else MISSING

                # Country Code
                country_code = None
                if "#" in location_name:
                    country_code = "<INACCESSIBLE>"
                else:
                    country_code = "US"

                # Store Number
                store_number = (
                    store_data["storeNumber"] if store_data["storeNumber"] else MISSING
                )

                # Phone
                phone = (
                    "("
                    + store_data["phone"][0:3]
                    + ") "
                    + store_data["phone"][3:6]
                    + "-"
                    + store_data["phone"][6:10]
                )
                if "() -" in phone:
                    phone = MISSING
                phone = phone if phone else MISSING

                # Location Type
                location_type = ""
                if store_data["brand"]:
                    location_type = (
                        store_data["brand"]
                        .replace("0", "")
                        .replace("1", "")
                        .replace("2", "")
                        .replace("3", "")
                        .replace("4", "")
                        .replace("5", "")
                        .replace("6", "")
                        .replace("7", "")
                        .replace("8", "")
                        .replace("9", "")
                        .strip()
                    )
                else:
                    location_type = MISSING

                # Latitude
                latitude = store_data["latitude"] if store_data["latitude"] else MISSING

                # Longitude
                longitude = (
                    store_data["longitude"] if store_data["longitude"] else MISSING
                )

                # Hours of Operation
                session = SgRequests()
                hours_request = session.get(
                    "http://find.cashamerica.us/api/stores/"
                    + str(store_data["storeNumber"])
                    + "?key="
                    + key,
                    headers=headers,
                )
                hours_details = hours_request.json()["weeklyHours"]
                hours = ""
                for k in range(len(hours_details)):
                    if hours_details[k]["openTime"] != "Closed":
                        hours = (
                            hours
                            + " "
                            + hours_details[k]["weekDay"]
                            + " "
                            + hours_details[k]["openTime"]
                            + " "
                            + hours_details[k]["closeTime"]
                            + " "
                        )
                hours_of_operation = hours.strip() if hours != "" else MISSING

                # Raw Address
                raw_address = MISSING
                item = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipcode,
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
    except Exception as e:
        logger.info(f"Please fix this error: <{e}> for < {url_data} >")


def get_api_key():
    with SgRequests() as http:
        url_key = "http://find.cashamerica.us/js/controllers/StoreMapController.js"
        logger.info(f"Extract key from: {url_key}")
        r = http.get(url_key, headers=headers)
        key = r.text.split("&key=")[1].split('");')[0]

        if key:
            logger.info(f"Key Found: {key}")
            return key
        else:
            logger.info(f"Unable to find the Key, please check the {url_key}")


def get_api_endpoint_urls():
    api_endpoint_urls = []
    url_store = "http://find.cashamerica.us/api/stores?p="
    api_key = get_api_key()
    start = 1
    total_page_number = 2800
    items_num_per_page = 1
    for page in range(start, total_page_number):
        url_data = f"{url_store}{str(page)}&s={items_num_per_page}&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key={str(api_key)}"
        api_endpoint_urls.append(url_data)
    return api_endpoint_urls, api_key


def fetch_data(sgw: SgWriter):
    api_urls, api_key = get_api_endpoint_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_global = [
            executor.submit(fetch_records, api_key, urlpartnum, urlpart, sgw)
            for urlpartnum, urlpart in enumerate(api_urls[0:])
        ]
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
