import re
import json
import csv
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "slimchickens.com"
BASE_URL = "https://slimchickens.com"
LOCATION_URL = "https://slimchickens.com/location-Menus/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()


def write_output(data):
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_json(link_url, js_variable):
    log.info("Pull content => " + link_url)
    soup = pull_content(link_url)
    pattern = re.compile(
        r"var\s+" + js_variable + "\\s*=\\s*(\\{.*?\\});", re.MULTILINE | re.DOTALL
    )
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"(?s)var\s+" + js_variable + "\\s*=\\s*(\\{.*?\\});", info)
    data = json.loads(parse.group(1))
    return data


def get_postal(address, country_code):
    if country_code == "US":
        check_postal = re.findall(r".*(\d{5}(\-\d{4})?)$", address)
        if check_postal:
            zip_code = check_postal[0][0]
        else:
            zip_code = None
    else:
        check_postal = re.findall(r"[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}", address)
        if check_postal:
            zip_code = check_postal[0]
        else:
            zip_code = None
    return zip_code


def get_address(full_address, country_code):
    log.info("Fetching store adress: {} => {}".format(country_code, full_address))
    data = full_address.encode().decode("utf-8").replace(u"\u2022", ",")
    split_addr = data.split(",")
    if country_code == "US":
        zip_code = get_postal(full_address, country_code)
        if not zip_code:
            zip_code = re.findall(r"\d+", split_addr[-1])[0]
        if len(split_addr) > 4:
            street_address = ",".join(split_addr[2:4])
            city = split_addr[0]
            state = split_addr[1]
        else:
            if len(split_addr) <= 3:
                parsed_addr = usaddress.parse(full_address)
                dict_address = dict(parsed_addr)
                split_addr = ",".join(dict_address).split(",")
                city = split_addr[0]
                state = split_addr[1]
                street_address = " ".join(split_addr[2:]).replace(zip_code, "")
            else:
                street_address = split_addr[2]
                city = split_addr[0]
                state = split_addr[1]
    else:
        city = split_addr[0]
        state = split_addr[1]
        if len(split_addr) > 4:
            street_address = ",".join(split_addr[2:4])
        else:
            street_address = split_addr[2]
        check_postal = re.findall(
            r"[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}", full_address
        )
        if check_postal:
            zip_code = check_postal[0]
        else:
            zip_code = None
    return {
        "street_address": street_address,
        "city": city,
        "state": state.replace(" ", ""),
        "zip_code": zip_code,
    }


def fetch_data():
    log.info("Fetching store URL")
    locations = []
    info = parse_json(LOCATION_URL, "maplistScriptParamsKo")
    for data in info["KOObject"][0]["locations"]:
        if "coming-soon" not in data["cssClass"]:
            location_name = handle_missing(
                data["title"].encode().decode("utf-8").replace(u"\u2022", ",")
            )
            latitude = handle_missing(data["latitude"])
            longitude = handle_missing(data["longitude"])
            page_url = data["locationUrl"]
            check_country = usaddress.tag(data["categories"][0]["title"])
            if (
                "CountryName" in check_country[0]
                and check_country[0]["CountryName"] != "Kansas"
            ):
                country_code = check_country[0]["CountryName"]
            else:
                country_code = "US"
            if "Kuwait" not in country_code:
                parsed_addr = get_address(location_name, country_code)
                street_address = handle_missing(parsed_addr["street_address"])
                city = handle_missing(parsed_addr["city"])
                state = handle_missing(data["categories"][0]["title"])
                zip_code = handle_missing(parsed_addr["zip_code"])
                location_type = "<MISSING>"
                store_number = data["cssClass"].split("loc-", 1)[1]
                if country_code == "US":
                    soup = bs(data["description"], "html.parser")
                    phone_pattren = r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
                    get_phone = soup.find(text=re.compile(phone_pattren))
                    if get_phone:
                        phone = get_phone.strip()
                    else:
                        content = soup.find_all("p")
                        get_phone = (
                            content[0].get_text(strip=True).replace("Phone:", "")
                        )
                        phone = "<MISSING>" if len(get_phone) > 15 else get_phone
                    hours = soup.find(text=re.compile(r".*([0-9]+)am.*", re.IGNORECASE))
                    hours_of_operation = handle_missing(
                        re.sub(r".?(7 days/week).*", "", hours.strip())
                    )
                else:
                    if "location" in page_url:
                        soup = pull_content(page_url)
                        content = soup.find_all(
                            "div",
                            {"class": "wpb_column vc_column_container vc_col-sm-4"},
                        )
                        if content:
                            hours_of_operation = handle_missing(
                                content[0]
                                .find("div", {"class": "vc_column-inner"})
                                .find(
                                    "div",
                                    {"class": "wpb_text_column wpb_content_element"},
                                )
                                .get_text(strip=True)
                                .replace("HOURS:", "")
                            )
                            phone = handle_missing(
                                content[1]
                                .find("div", {"class": "vc_column-inner"})
                                .find(
                                    "div",
                                    {"class": "wpb_text_column wpb_content_element"},
                                )
                                .get_text(strip=True)
                                .replace("PHONE:", "")
                            )
                        else:
                            hours_of_operation = "<MISSING>"
                            phone = "<MISSING>"
                log.info("Append info to locations => " + location_name)
                locations.append(
                    [
                        DOMAIN,
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
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
