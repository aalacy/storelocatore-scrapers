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
logger = SgLogSetup().get_logger("openchargemap_org___hash_americas")
MISSING = SgRecord.MISSING
MAX_WORKERS = 6
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
    {"country_name": "Anguilla", "continent_code": "NA", "country_code": "AI"},
    {
        "country_name": "Antigua and Barbuda",
        "continent_code": "NA",
        "country_code": "AG",
    },
    {"country_name": "Argentina", "continent_code": "SA", "country_code": "AR"},
    {"country_name": "Aruba", "continent_code": "NA", "country_code": "AW"},
    {"country_name": "Bahamas", "continent_code": "NA", "country_code": "BS"},
    {"country_name": "Barbados", "continent_code": "NA", "country_code": "BB"},
    {"country_name": "Belize", "continent_code": "NA", "country_code": "BZ"},
    {"country_name": "Bermuda", "continent_code": "NA", "country_code": "BM"},
    {"country_name": "Bolivia", "continent_code": "SA", "country_code": "BO"},
    {"country_name": "Bonaire", "continent_code": "NA", "country_code": "BQ"},
    {"country_name": "Brazil", "continent_code": "SA", "country_code": "BR"},
    {
        "country_name": "British Virgin Islands",
        "continent_code": "NA",
        "country_code": "VG",
    },
    {"country_name": "Cayman Islands", "continent_code": "NA", "country_code": "KY"},
    {"country_name": "Chile", "continent_code": "SA", "country_code": "CL"},
    {"country_name": "Colombia", "continent_code": "SA", "country_code": "CO"},
    {"country_name": "Costa Rica", "continent_code": "NA", "country_code": "CR"},
    {"country_name": "Cuba", "continent_code": "NA", "country_code": "CU"},
    {"country_name": "Curaçao", "continent_code": "NA", "country_code": "CW"},
    {"country_name": "Dominica", "continent_code": "NA", "country_code": "DM"},
    {
        "country_name": "Dominican Republic",
        "continent_code": "NA",
        "country_code": "DO",
    },
    {"country_name": "Ecuador", "continent_code": "SA", "country_code": "EC"},
    {"country_name": "El Salvador", "continent_code": "NA", "country_code": "SV"},
    {
        "country_name": "Falkland Islands (Malvinas)",
        "continent_code": "SA",
        "country_code": "FK",
    },
    {"country_name": "French Guiana", "continent_code": "SA", "country_code": "GF"},
    {"country_name": "Greenland", "continent_code": "NA", "country_code": "GL"},
    {"country_name": "Grenada", "continent_code": "NA", "country_code": "GD"},
    {"country_name": "Guadeloupe", "continent_code": "NA", "country_code": "GP"},
    {"country_name": "Guatemala", "continent_code": "NA", "country_code": "GT"},
    {"country_name": "Guyana", "continent_code": "SA", "country_code": "GY"},
    {"country_name": "Haiti", "continent_code": "NA", "country_code": "HT"},
    {"country_name": "Honduras", "continent_code": "NA", "country_code": "HN"},
    {"country_name": "Jamaica", "continent_code": "NA", "country_code": "JM"},
    {"country_name": "Martinique", "continent_code": "NA", "country_code": "MQ"},
    {"country_name": "Mexico", "continent_code": "NA", "country_code": "MX"},
    {"country_name": "Montserrat", "continent_code": "NA", "country_code": "MS"},
    {"country_name": "Nicaragua", "continent_code": "NA", "country_code": "NI"},
    {"country_name": "Panama", "continent_code": "NA", "country_code": "PA"},
    {"country_name": "Paraguay", "continent_code": "SA", "country_code": "PY"},
    {"country_name": "Peru", "continent_code": "SA", "country_code": "PE"},
    {"country_name": "Puerto Rico", "continent_code": "NA", "country_code": "PR"},
    {"country_name": "Saint Barthelemy", "continent_code": "NA", "country_code": "BL"},
    {
        "country_name": "Saint Kitts and Nevis",
        "continent_code": "NA",
        "country_code": "KN",
    },
    {"country_name": "Saint Lucia", "continent_code": "NA", "country_code": "LC"},
    {"country_name": "Saint Martin", "continent_code": "NA", "country_code": "MF"},
    {
        "country_name": "Saint Pierre and Miquelon",
        "continent_code": "NA",
        "country_code": "PM",
    },
    {
        "country_name": "Saint Vincent and the Grenadines",
        "continent_code": "NA",
        "country_code": "VC",
    },
    {
        "country_name": "Sint Maarten (Netherlands)",
        "continent_code": "NA",
        "country_code": "SX",
    },
    {"country_name": "Suriname", "continent_code": "SA", "country_code": "SR"},
    {
        "country_name": "Trinidad and Tobago",
        "continent_code": "NA",
        "country_code": "TT",
    },
    {
        "country_name": "Turks and Caicos Islands",
        "continent_code": "NA",
        "country_code": "TC",
    },
    {
        "country_name": "United States Virgin Islands",
        "continent_code": "NA",
        "country_code": "VI",
    },
    {"country_name": "Uruguay", "continent_code": "SA", "country_code": "UY"},
    {"country_name": "Venezuela", "continent_code": "SA", "country_code": "VE"},
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
            location_name = ai["Title"] or MISSING
            street_address = ai["AddressLine1"] or MISSING
            city = ai["Town"] or MISSING
            state = ai["StateOrProvince"] or MISSING
            zip_postal = ai["Postcode"] or MISSING
            country_code = ai["Country"]["ISOCode"] or MISSING
            store_number = _["DataProvidersReference"] or MISSING
            latitude = ai["Latitude"] or MISSING
            longitude = ai["Longitude"] or MISSING
            phone = ai["ContactTelephone1"] or MISSING
            location_type = MISSING
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
