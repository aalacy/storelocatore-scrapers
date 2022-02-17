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
logger = SgLogSetup().get_logger("openchargemap_org___hash_asia-australia-oceania")
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
    {"country_name": "Afghanistan", "continent_code": "AS", "country_code": "AF"},
    {"country_name": "Armenia", "continent_code": "AS", "country_code": "AM"},
    {"country_name": "Azerbaijan", "continent_code": "AS", "country_code": "AZ"},
    {"country_name": "Bahrain", "continent_code": "AS", "country_code": "BH"},
    {"country_name": "Bangladesh", "continent_code": "AS", "country_code": "BD"},
    {"country_name": "Bhutan", "continent_code": "AS", "country_code": "BT"},
    {"country_name": "Brunei Darussalam", "continent_code": "AS", "country_code": "BN"},
    {"country_name": "Cambodia", "continent_code": "AS", "country_code": "KH"},
    {"country_name": "China", "continent_code": "AS", "country_code": "CN"},
    {"country_name": "Cyprus", "continent_code": "AS", "country_code": "CY"},
    {"country_name": "Georgia", "continent_code": "AS", "country_code": "GE"},
    {"country_name": "Hong Kong", "continent_code": "AS", "country_code": "HK"},
    {"country_name": "India", "continent_code": "AS", "country_code": "IN"},
    {"country_name": "Indonesia", "continent_code": "AS", "country_code": "ID"},
    {"country_name": "Iran", "continent_code": "AS", "country_code": "IR"},
    {"country_name": "Iraq", "continent_code": "AS", "country_code": "IQ"},
    {"country_name": "Israel", "continent_code": "AS", "country_code": "IL"},
    {"country_name": "Japan", "continent_code": "AS", "country_code": "JP"},
    {"country_name": "Jordan", "continent_code": "AS", "country_code": "JO"},
    {"country_name": "Kazakhstan", "continent_code": "AS", "country_code": "KZ"},
    {"country_name": "Korea", "continent_code": "AS", "country_code": "KP"},
    {"country_name": "Korea", "continent_code": "AS", "country_code": "KR"},
    {"country_name": "Kuwait", "continent_code": "AS", "country_code": "KW"},
    {"country_name": "Kyrgyz Republic", "continent_code": "AS", "country_code": "KG"},
    {
        "country_name": "Lao People's Democratic Republic",
        "continent_code": "AS",
        "country_code": "LA",
    },
    {"country_name": "Lebanon", "continent_code": "AS", "country_code": "LB"},
    {"country_name": "Macao", "continent_code": "AS", "country_code": "MO"},
    {"country_name": "Malaysia", "continent_code": "AS", "country_code": "MY"},
    {"country_name": "Maldives", "continent_code": "AS", "country_code": "MV"},
    {"country_name": "Mongolia", "continent_code": "AS", "country_code": "MN"},
    {"country_name": "Myanmar", "continent_code": "AS", "country_code": "MM"},
    {"country_name": "Nepal", "continent_code": "AS", "country_code": "NP"},
    {"country_name": "Oman", "continent_code": "AS", "country_code": "OM"},
    {"country_name": "Pakistan", "continent_code": "AS", "country_code": "PK"},
    {
        "country_name": "Palestinian Territory",
        "continent_code": "AS",
        "country_code": "PS",
    },
    {"country_name": "Philippines", "continent_code": "AS", "country_code": "PH"},
    {"country_name": "Qatar", "continent_code": "AS", "country_code": "QA"},
    {"country_name": "Saudi Arabia", "continent_code": "AS", "country_code": "SA"},
    {"country_name": "Singapore", "continent_code": "AS", "country_code": "SG"},
    {"country_name": "Sri Lanka", "continent_code": "AS", "country_code": "LK"},
    {
        "country_name": "Syrian Arab Republic",
        "continent_code": "AS",
        "country_code": "SY",
    },
    {"country_name": "Taiwan", "continent_code": "AS", "country_code": "TW"},
    {"country_name": "Tajikistan", "continent_code": "AS", "country_code": "TJ"},
    {"country_name": "Thailand", "continent_code": "AS", "country_code": "TH"},
    {"country_name": "Timor-Leste", "continent_code": "AS", "country_code": "TL"},
    {"country_name": "Turkey", "continent_code": "AS", "country_code": "TR"},
    {"country_name": "Turkmenistan", "continent_code": "AS", "country_code": "TM"},
    {
        "country_name": "United Arab Emirates",
        "continent_code": "AS",
        "country_code": "AE",
    },
    {"country_name": "Uzbekistan", "continent_code": "AS", "country_code": "UZ"},
    {"country_name": "Vietnam", "continent_code": "AS", "country_code": "VN"},
    {"country_name": "Yemen", "continent_code": "AS", "country_code": "YE"},
    {"country_name": "American Samoa", "continent_code": "OC", "country_code": "AS"},
    {"country_name": "Australia", "continent_code": "OC", "country_code": "AU"},
    {"country_name": "Cook Islands", "continent_code": "OC", "country_code": "CK"},
    {"country_name": "Fiji", "continent_code": "OC", "country_code": "FJ"},
    {"country_name": "French Polynesia", "continent_code": "OC", "country_code": "PF"},
    {"country_name": "Guam", "continent_code": "OC", "country_code": "GU"},
    {"country_name": "Kiribati", "continent_code": "OC", "country_code": "KI"},
    {"country_name": "Marshall Islands", "continent_code": "OC", "country_code": "MH"},
    {"country_name": "Micronesia", "continent_code": "OC", "country_code": "FM"},
    {"country_name": "Nauru", "continent_code": "OC", "country_code": "NR"},
    {"country_name": "New Caledonia", "continent_code": "OC", "country_code": "NC"},
    {"country_name": "New Zealand", "continent_code": "OC", "country_code": "NZ"},
    {"country_name": "Niue", "continent_code": "OC", "country_code": "NU"},
    {
        "country_name": "Northern Mariana Islands",
        "continent_code": "OC",
        "country_code": "MP",
    },
    {"country_name": "Palau", "continent_code": "OC", "country_code": "PW"},
    {"country_name": "Papua New Guinea", "continent_code": "OC", "country_code": "PG"},
    {"country_name": "Samoa", "continent_code": "OC", "country_code": "WS"},
    {"country_name": "Solomon Islands", "continent_code": "OC", "country_code": "SB"},
    {"country_name": "Tokelau", "continent_code": "OC", "country_code": "TK"},
    {"country_name": "Tonga", "continent_code": "OC", "country_code": "TO"},
    {"country_name": "Tuvalu", "continent_code": "OC", "country_code": "TV"},
    {"country_name": "Vanuatu", "continent_code": "OC", "country_code": "VU"},
    {"country_name": "Wallis and Futuna", "continent_code": "OC", "country_code": "WF"},
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
