import csv
import re
import json
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "handymart.com"
BASE_URL = "https://www.handymart.com"
LOCATION_URL = "http://www.handymart.com/locations_handymart/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def write_output(data):
    log.info("Write Output of " + DOMAIN)
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_json(soup, js_variable):
    pattern = re.compile(
        r"var\s+" + js_variable + r"\s+= \{.*?\}", re.MULTILINE | re.DOTALL
    )
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"var\s+" + js_variable + r"\s+= (\{.*?\});", info)
    parse = parse.group(1)
    data = json.loads(parse)
    return data


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_address = (
        soup.find("table", {"class": "table table-bordered table-striped"})
        .find("tbody")
        .find_all("tr")
    )
    store_info = parse_json(soup, "wpgmaps_localize_marker_data")
    locations = []
    for index in store_info:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = "Handy Mart"
        address = store_info[index]["address"].replace("City", "").split(",")
        if len(address) >= 3:
            street_address = address[0].strip()
            city = address[1].strip()
            state = re.sub(r"\d+", "", address[2]).replace("\u200e", "").strip()
            zip_code = re.sub(r"\D+", "", address[2]).strip()
        else:
            parse_address = usaddress.tag(
                store_info[index]["address"].replace("City", "")
            )
            city = parse_address[0]["PlaceName"]
            street_address = address[0].replace(city, "").strip()
            state = re.sub(r"\d+", "", address[1]).replace("\u200e", "").strip()
            zip_code = re.sub(r"\D+", "", address[1]).strip()
        country_code = "US"
        store_number = index
        get_phone = soup.find("td", string=re.compile(address[0][:5] + r".*"))
        if get_phone:
            phone = get_phone.find_next("td").text.strip()
        else:
            get_phone = soup.find("td", string=re.compile(address[0][:3] + r".*"))
            phone = get_phone.find_next("td").text.strip()
        hours_of_operation = "<MISSING>"
        location_type = get_phone.parent()[0].find("img")["alt"].strip()
        latitude = handle_missing(store_info[index]["lat"])
        longitude = handle_missing(store_info[index]["lat"])
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    last_element = store_address[-1].find_all("td")
    if last_element[2].text not in [val[3] for val in locations]:
        address = last_element[1].text.strip().split(",")
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
                LOCATION_URL,
                "Handy Mart",
                address[0],
                address[1],
                address[2],
                "<MISSING>",
                "US",
                "22",
                last_element[2].text.strip(),
                last_element[0].find("img")["alt"].strip(),
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            ]
        )
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
