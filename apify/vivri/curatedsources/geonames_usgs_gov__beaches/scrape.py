import csv
import zipfile
import io
from os import listdir
from bs4 import BeautifulSoup
from concurrent.futures import *
from sgscrape import simple_network_utils
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('geonames.usgs.gov_beaches')

MISSING = "<MISSING>"
FEATURE_URL_PREFIX = 'https://geonames.usgs.gov/apex/f?p=138:3:::NO:3:P3_FID,P3_TITLE:'

def mk_writer(output_file):
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    # Header
    writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
    return writer

def fetch_national_file() -> None:
    # TODO - optimize by storing it in memory
    session = SgRequests()
    stream_res = session.get("https://geonames.usgs.gov/docs/stategaz/NationalFile.zip", stream=True)
    z = zipfile.ZipFile(io.BytesIO(stream_res.content))
    z.extractall(".")

def find_filename() -> str:
    return [f for f in listdir('.') if f.startswith('NationalFile_')][0]

def read_national_file(filename: str) -> list:
    with open(filename) as csvfile:
        rows = csv.reader(csvfile, delimiter='|')
        for row in rows:
            if row[2] == 'Beach':
                yield row[0].strip()

def or_else(try_get: lambda: str, otherwise: str = MISSING) -> str:
    try:
        value = try_get().strip()
        return value if value else otherwise
    except:
        return otherwise

def get_sibling_value(xml_result, name_of_value: str) -> str:
    left = xml_result.find_all(name="td", attrs={"class": "L"}, text=name_of_value)[0]
    return left.next_sibling.text.strip()

def page_url(feature_id: str) -> str:
    return f"{FEATURE_URL_PREFIX}{feature_id}"

def fetch_data(feature_id: str):
    pageurl = page_url(feature_id)
    try:
        raw_data = simple_network_utils.fetch_data(request_url=pageurl)
        return feature_id, pageurl, raw_data

    except Exception as e:
        logger.error(f"Error while fetching from {page_url}", exc_info=e)
        return None

def parse_record_data(feature_id: str, pageurl: str, raw_response) -> list:
    locator_domain = "https://geonames.usgs.gov"
    phone = MISSING
    store_number = feature_id
    location_type = MISSING
    hours_of_operation = MISSING

    xml_result = BeautifulSoup(raw_response.text, 'lxml')

    location_name = get_sibling_value(xml_result, "Name:")

    street_address = or_else(lambda: or_else(lambda: get_sibling_value(xml_result, "Address:"), location_name))
    city = or_else(lambda: get_sibling_value(xml_result, "City:"))
    zipcode = or_else(lambda: get_sibling_value(xml_result, "ZIP:"))

    state = xml_result.find("td", attrs={"headers": "STATE_NAME"}).text.strip()
    latitude = xml_result.find("td", attrs={"headers": "LAT"}).text.strip()
    longitude = xml_result.find("td", attrs={"headers": "LONGI"}).text.strip()
    country_code = xml_result.find("td", attrs={"headers": "COUNTRY_ALPHA"}).text.strip()

    return [locator_domain, pageurl, location_name, street_address, city, state, zipcode, country_code,
            store_number, phone, location_type, latitude, longitude, hours_of_operation]

def scrape():
    fetch_national_file()
    with open('data.csv', mode='w') as output_file:
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix='fetcher') as executor:
            writer = mk_writer(output_file)
            national_file_data = read_national_file(find_filename())
            for ret in executor.map(fetch_data, national_file_data):
                if ret:
                    feature_id, pageurl, raw_data = ret
                    record = parse_record_data(feature_id=feature_id, pageurl=pageurl, raw_response=raw_data)
                    if record:
                        writer.writerow(record)

if __name__ == "__main__":
    scrape()
