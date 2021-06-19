import re
import csv
import json
from re import IGNORECASE
import time
import simplejson
import threading
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("cvs_com")


start_time = datetime.now()

thread_local = threading.local()
base_url = "https://www.cvs.com"

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "connection": "Keep-Alive",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "location_type",
                "store_number",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "latitude",
                "longitude",
                "phone",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)

    end_time = datetime.now()
    timedelta = end_time - start_time
    logger.info("--------------------")
    duration = time.strftime("%H:%M:%S", time.gmtime(timedelta.total_seconds()))
    logger.info(f"duration: {duration}")


def get_session():
    if (
        not hasattr(thread_local, "session")
        or thread_local.request_count > 5
        or thread_local.session_failed
    ):
        thread_local.session = SgRequests()
        thread_local.request_count = 0
        thread_local.session_failed = False

    thread_local.request_count += 1
    return thread_local.session


def mark_session_failed():
    thread_local.session_failed = True


def is_valid(soup):
    is_valid = soup.select_one("#header") or soup.select_one(".pharmacy-logo")
    if not is_valid:
        mark_session_failed()

    return is_valid


@retry(reraise=True, stop=stop_after_attempt(5))
def enqueue_links(url, selector):
    urls = []
    get_session()
    r = session.get(url, headers=headers)
    if r.status_code != 200:
        r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    if not is_valid(soup):
        raise Exception(f"Unable to extract data from {url}")

    links = soup.select(selector)

    for link in links:
        lurl = urljoin(base_url, link["href"])
        urls.append(lurl)

    return urls


def scrape_state_urls(state_urls):
    city_urls = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(enqueue_links, url, ".states a") for url in state_urls
        ]
        for future in as_completed(futures):
            urls = future.result()
            city_urls.extend(urls)

    return city_urls


def scrape_city_urls(city_urls):
    # scrape each city url and populate loc_urls with the results
    loc_urls = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(enqueue_links, url, ".directions-link a")
            for url in city_urls
        ]
        for future in as_completed(futures):
            urls = future.result()
            loc_urls.extend(urls)

    return loc_urls


def parse_details(node):
    props = json.loads(node["sd-props"])
    return props["cvsMyStoreDetailsProps"]


def parse_store(node, loc=None):
    try:
        props = json.loads(node["sd-props"])
        return props["cvsMyStoreDetailsProps"]["store"]
    except:
        match = re.search(r'"store":\s*(\{(\n|.)*?\}`),', str(node), re.IGNORECASE)
        return json.loads(match.group(1))


def extract_value(key, html):
    match = re.search(fr'"{key}":\s*"(.*)"', html, re.IGNORECASE)
    return match.group(1) if match else None


@retry(reraise=True, stop=stop_after_attempt(3))
def get_basic_info(id, page_schema, location, session):
    address = None
    try:
        data = {"storeId": id}
        result = session.post(
            "https://www.cvs.com/rest/bean/cvs/store/CvsStoreLocatorServices/getStoreIdDetails",
            data=data,
        ).json()

        info = result["atgResponse"]["sm"]
        address = {
            "street_address": info["ad"].strip(),
            "city": info["ci"].strip(),
            "state": info["st"].strip(),
            "postal": info["zp"].strip(),
            "phone": info["ph"].strip(),
            "country_code": "US",
        }
    except simplejson.decoder.JSONDecodeError:
        try:
            node = location.find("cvs-store-details")
            props = json.loads(node["sd-props"])
            store = props["cvsMyStoreDetailsProps"]["store"]
            address = {
                "street_address": store["addressLine"].strip(),
                "city": store["addressCityDescriptionText"].strip(),
                "state": store["addressState"].strip(),
                "postal": store["addressZipCode"].strip(),
                "phone": store["phoneNumber"].strip(),
                "country_code": "US",
            }
        except:
            addr = page_schema["address"]
            address = {
                "street_address": addr["streetAddress"].strip(),
                "city": addr["addressLocality"].strip(),
                "state": addr["addressRegion"].strip(),
                "postal": addr["postalCode"].strip(),
                "phone": addr["telephone"].strip(),
                "country_code": addr["addressCountry"].strip(),
            }
    # parsing directional data from street address
    if "," in address["street_address"]:
        street_address, *others = re.split(",", address["street_address"])
        address["street_address"] = street_address

    return address


def get_geolocation(location, page_schema):
    details = re.sub("&quot;", '"', str(location))

    latitude = (
        extract_value("lat", details)
        or extract_value("geographicLatitudePoint", details)
        or page_schema["geo"]["latitude"]
    )

    longitude = (
        extract_value("lng", details)
        or extract_value("geographicLongitudePoint", details)
        or page_schema["geo"]["longitude"]
    )

    if not latitude or not longitude:
        try:
            coord = json.loads(location.find("cvs-map")["map-props"])["pinsArray"][0]
            latitude = coord["lat"]
            longitude = coord["lng"]
        except:
            latitude = None
            longitude = None
    try:
        latitude = float(latitude) or None
        longitude = float(longitude) or None
    except:
        latitude = None
        longitude = None

    return {"latitude": latitude, "longitude": longitude}


def is_valid_hours(hour_text):
    return re.search(r"\d+|closed", hour_text, re.IGNORECASE)


def get_hours(location, page_schema):
    node = location.find("cvs-store-details")
    try:
        details = json.loads(node["sd-props"])
        store_hours = details["cvsLocationHoursProps"]["locationHours"]
        location_hours = store_hours[0]["hours"]

        if not len(location_hours) and len(store_hours) > 1:
            location_hours = store_hours[1]["hours"]

    except (TypeError, json.decoder.JSONDecodeError):
        try:
            details = re.sub("&quot;", '"', str(node))
            serialized = re.search(
                r'"locationHours":\s*(\[(.|\n)+\])(.|\n)*"cvsCtaAreaProps',
                details,
                re.IGNORECASE,
            ).group(1)
            location_hours = json.loads(serialized)[0]["hours"]
        except (TypeError, AttributeError):
            try:
                hour_text = ",".join(page_schema["openingHours"])
                return hour_text if is_valid_hours(hour_text) else MISSING

            except Exception as e:
                logger.error(e)
                return MISSING

    if not len(location_hours):
        return MISSING

    hours = []
    for hour in location_hours:
        day = hour["titleText"]
        if re.search("today", day, re.IGNORECASE):
            continue
        
        start = hour['startTime']
        end = hour['endTime']
        timerange =  start if re.search('open 24 hours', start, re.IGNORECASE) else f"{start}-{end}"

        hours.append(f"{day}: {timerange}")

    hours_of_operation = ",".join(hours)
    return hours_of_operation if is_valid_hours(hours_of_operation) else MISSING


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


@retry(reraise=True, stop=stop_after_attempt(5))
def get_location(page_url):
    try:
        session = get_session()
        r = session.get(page_url, headers=headers)
        location = BeautifulSoup(r.text, "lxml")

        if not is_valid(location):
            raise Exception(f"Unable to extract data from {page_url}")

        script = location.select_one("#structured-data-block")
        if not script:
            raise Exception(f"Unable to extract data from {page_url}")

        structured_data = script.string
        store_number = re.search(r"(storeid=|details-directions\/)(\d+)", page_url).group(2)
        page_schema = json.loads(structured_data)[0]
        basic_info = get_basic_info(store_number, page_schema, location, session)
        geolocation = get_geolocation(location, page_schema)
        hours_of_operation = get_hours(location, page_schema)

        locator_domain = "csv.com"
        location_name = get(page_schema, "name")
        location_type = get(page_schema, "@type")
        street_address = get(basic_info, "street_address")
        city = get(basic_info, "city")
        state = get(basic_info, "state")
        postal = get(basic_info, "postal")
        phone = get(basic_info, "phone")
        country_code = get(basic_info, "country_code")
        latitude = get(geolocation, "latitude")
        longitude = get(geolocation, "longitude")

        return [
            locator_domain,
            page_url,
            location_name,
            location_type,
            store_number,
            street_address,
            city,
            state,
            postal,
            country_code,
            latitude,
            longitude,
            phone,
            hours_of_operation,
        ]
    except Exception as e:
        logger.error(f'{e} >>> {page_url}')

def scrape_loc_urls(loc_urls):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_location, loc) for loc in loc_urls]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    yield record
            except Exception as e:
                logger.error(str(e))


def fetch_data():
    state_urls = enqueue_links(
        urljoin(base_url, "/store-locator/cvs-pharmacy-locations"), ".states a"
    )

    # logger.info(f"number of states: {len(state_urls)}")
    # city_urls = scrape_state_urls(state_urls)

    # logger.info(f"number of cities: {len(city_urls)}")
    # loc_urls = scrape_city_urls(city_urls)

    with open('locations.json') as file:
        loc_urls = json.load(file)

    logger.info(f"number of locations: {len(loc_urls)}")
    return scrape_loc_urls(loc_urls)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
