from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
import tenacity
import time
import ssl
import random

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "openchargemap.org"
logger = SgLogSetup().get_logger("openchargemap_org___hash_eu")
MISSING = SgRecord.MISSING
MAX_WORKERS = 8
BASE_API = (
    "https://api.openchargemap.io/v3/poi/?client=ocm.app.ionic.8.0.0&verbose=true"
)
# Latest API KEY created 31 October 2021
API_KEY = "7f54c350-21c5-42fe-9614-c768c4147509"
MAX_RESULTS = 50000

headers = {
    "user-agent": "Openchargemap Data",
}

country_list = [
    {"country_name": "Åland Islands", "continent_code": "EU", "country_code": "AX"},
    {"country_name": "Albania", "continent_code": "EU", "country_code": "AL"},
    {"country_name": "Andorra", "continent_code": "EU", "country_code": "AD"},
    {"country_name": "Armenia", "continent_code": "EU", "country_code": "AM"},
    {"country_name": "Austria", "continent_code": "EU", "country_code": "AT"},
    {"country_name": "Azerbaijan", "continent_code": "EU", "country_code": "AZ"},
    {"country_name": "Belarus", "continent_code": "EU", "country_code": "BY"},
    {"country_name": "Belgium", "continent_code": "EU", "country_code": "BE"},
    {
        "country_name": "Bosnia and Herzegovina",
        "continent_code": "EU",
        "country_code": "BA",
    },
    {"country_name": "Bulgaria", "continent_code": "EU", "country_code": "BG"},
    {"country_name": "Croatia", "continent_code": "EU", "country_code": "HR"},
    {"country_name": "Cyprus", "continent_code": "EU", "country_code": "CY"},
    {"country_name": "Czech Republic", "continent_code": "EU", "country_code": "CZ"},
    {"country_name": "Denmark", "continent_code": "EU", "country_code": "DK"},
    {"country_name": "Estonia", "continent_code": "EU", "country_code": "EE"},
    {"country_name": "Faroe Islands", "continent_code": "EU", "country_code": "FO"},
    {"country_name": "Georgia", "continent_code": "EU", "country_code": "GE"},
    {"country_name": "Gibraltar", "continent_code": "EU", "country_code": "GI"},
    {"country_name": "Greece", "continent_code": "EU", "country_code": "GR"},
    {"country_name": "Guernsey", "continent_code": "EU", "country_code": "GG"},
    {
        "country_name": "Holy See (Vatican City State)",
        "continent_code": "EU",
        "country_code": "VA",
    },
    {"country_name": "Hungary", "continent_code": "EU", "country_code": "HU"},
    {"country_name": "Iceland", "continent_code": "EU", "country_code": "IS"},
    {"country_name": "Ireland", "continent_code": "EU", "country_code": "IE"},
    {"country_name": "Isle of Man", "continent_code": "EU", "country_code": "IM"},
    {"country_name": "Jersey", "continent_code": "EU", "country_code": "JE"},
    {"country_name": "Kazakhstan", "continent_code": "EU", "country_code": "KZ"},
    {"country_name": "Latvia", "continent_code": "EU", "country_code": "LV"},
    {"country_name": "Liechtenstein", "continent_code": "EU", "country_code": "LI"},
    {"country_name": "Lithuania", "continent_code": "EU", "country_code": "LT"},
    {"country_name": "Luxembourg", "continent_code": "EU", "country_code": "LU"},
    {"country_name": "Macedonia", "continent_code": "EU", "country_code": "MK"},
    {"country_name": "Malta", "continent_code": "EU", "country_code": "MT"},
    {"country_name": "Moldova", "continent_code": "EU", "country_code": "MD"},
    {"country_name": "Monaco", "continent_code": "EU", "country_code": "MC"},
    {"country_name": "Montenegro", "continent_code": "EU", "country_code": "ME"},
    {"country_name": "Norway", "continent_code": "EU", "country_code": "NO"},
    {"country_name": "Poland", "continent_code": "EU", "country_code": "PL"},
    {"country_name": "Portugal", "continent_code": "EU", "country_code": "PT"},
    {"country_name": "Romania", "continent_code": "EU", "country_code": "RO"},
    {
        "country_name": "Russian Federation",
        "continent_code": "EU",
        "country_code": "RU",
    },
    {"country_name": "San Marino", "continent_code": "EU", "country_code": "SM"},
    {"country_name": "Serbia", "continent_code": "EU", "country_code": "RS"},
    {
        "country_name": "Slovakia (Slovak Republic)",
        "continent_code": "EU",
        "country_code": "SK",
    },
    {"country_name": "Slovenia", "continent_code": "EU", "country_code": "SI"},
    {"country_name": "Spain", "continent_code": "EU", "country_code": "ES"},
    {
        "country_name": "Svalbard & Jan Mayen Islands",
        "continent_code": "EU",
        "country_code": "SJ",
    },
    {"country_name": "Sweden", "continent_code": "EU", "country_code": "SE"},
    {"country_name": "Switzerland", "continent_code": "EU", "country_code": "CH"},
    {"country_name": "Turkey", "continent_code": "EU", "country_code": "TR"},
    {"country_name": "Ukraine", "continent_code": "EU", "country_code": "UA"},
]

# Tenacity needs to be used b/c sometimes it experiences HTTP Error 500.
# It is found that after 3/4/5 retries, the request gets through with SUCCESS


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(10))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        logger.info(f"Status Code: {response.status_code}")
        time.sleep(random.randint(10, 30))
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_api_urls():
    api_urls = []
    for idx, country_a2 in enumerate(country_list[0:]):
        API_ENDPOINT_URL = f"{BASE_API}&key={str(API_KEY)}&output=json&countrycode={str(country_a2['country_code'])}&maxresults={str(MAX_RESULTS)}&compact=false"
        api_urls.append((country_a2["country_code"], API_ENDPOINT_URL))
    return api_urls


def get_custom_locname(_):
    location_name = ""
    if "OperatorInfo" in _ and _["OperatorInfo"] is not None:
        try:
            if "Title" in _["OperatorInfo"]:
                ln = _["OperatorInfo"]["Title"]
                if ln is not None:
                    location_name = ln + " " + "Charging Station"
                else:
                    location_name = MISSING
            else:
                location_name = MISSING
        except:
            location_name = MISSING
    else:
        location_name = "OperatorInfo Unavailable"
    return location_name


def remove_parenthesis_n_string(locname):
    ln = None
    if "(" in locname and ")" in locname:
        ln1 = locname.split("(")[0].strip()
        ln2 = locname.split("(")[-1].strip()
        ln3 = ln2.split(")")[-1].strip()
        ln4 = ln1 + " " + ln3
        ln = ln4.strip()
    else:
        ln = locname
    return ln


def get_custom_location_type(_):
    location_type = ""
    if "StatusType" in _:
        try:
            if "IsOperational" in _["StatusType"]:
                lt = _["StatusType"]["IsOperational"]
                if lt is not None:
                    location_type = "IsOperational: " + str(lt)
                else:
                    location_type = MISSING
            else:
                location_type = MISSING
        except:
            location_type = MISSING
    else:
        location_type = MISSING
    return location_type


def fetch_records(url_country, sgw: SgWriter):
    store_count_total = 0
    url = url_country[1]
    country = url_country[0]
    logger.info(f"Pulling the data | {country} | {url}")
    r = get_response(url)
    logger.info(f"HTTP Status: {r.status_code}")
    logger.info(f"Pulling the data from : {url}")
    if r.status_code == 200:
        data = r.json()
        store_count_per_country = len(data)
        store_count_total += store_count_per_country
        logger.info(f"Store Count: | {store_count_per_country} | {country} |")
        logger.info(f"Total Store Count: {store_count_total}")
        for _ in data:
            locator_domain = DOMAIN
            ai = _["AddressInfo"]

            # Custom Location Name
            locname = get_custom_locname(_)
            location_name = remove_parenthesis_n_string(locname)
            street_address = ai["AddressLine1"] or MISSING
            city = ai["Town"] or MISSING
            state = ai["StateOrProvince"] or MISSING
            zip_postal = ai["Postcode"] or MISSING
            country_code = ai["Country"]["ISOCode"] or MISSING
            store_number = _["DataProvidersReference"] or MISSING
            latitude = ai["Latitude"] or MISSING
            longitude = ai["Longitude"] or MISSING
            phone = ai["ContactTelephone1"] or MISSING

            # Custom Location Type
            location_type = get_custom_location_type(_)
            hours_of_operation = MISSING
            raw_address = MISSING
            page_url = ai["RelatedURL"] or MISSING
            rec = SgRecord(
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
            sgw.write_row(rec)
    logger.info(f"Total Store Count: {store_count_total}")


def fetch_data(sgw: SgWriter):
    urls = get_api_urls()
    logger.info(f"All API Endpoint URLs: {urls}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, url_country, sgw) for url_country in urls
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
