import csv
import json
import re
from sgselenium import SgSelenium
from sglogging import sglog

DOMAIN = "londondrugs.com"
BASE_URL = "https://www.londondrugs.com"
LOCATION_URL = "https://www.londondrugs.com/store-locations/?context=storeLocator"
API_URL = "https://www.londondrugs.com/on/demandware.store/Sites-LondonDrugs-Site/default/MktStoreList-All"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
driver = SgSelenium().chrome()


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
    driver.get(url)
    return driver


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def get_hours(hoo):
    hours = ""
    for x in hoo:
        if x["type"] == "Store Hours":
            for y in x["storeHours"]:
                hours += "{}: {}, ".format(y["day"], " - ".join(y["hours"]))
    return re.sub(", $", "", hours)


def fetch_store_urls():
    driver = pull_content(LOCATION_URL)
    main = driver.find_elements_by_css_selector("div.all-stores")
    store_info = []
    for row in main:
        lists = row.find_elements_by_css_selector("li")
        for li in lists:
            link = li.find_element_by_css_selector(
                "a.ld-sg-link[itemprop='name']"
            ).get_attribute("href")
            name = li.find_element_by_css_selector(
                "a.ld-sg-link[itemprop='name']"
            ).text.strip()
            street_address = li.find_element_by_css_selector(
                "span[itemprop='streetAddress']"
            ).text.strip()
            city = li.find_element_by_css_selector(
                "span[itemprop='addressLocality']"
            ).text.strip()
            state = li.find_element_by_css_selector(
                "span[itemprop='addressRegion']"
            ).text.strip()
            zip_code = li.find_element_by_css_selector(
                "span[itemprop='postalCode']"
            ).text.strip()
            phone = li.find_element_by_css_selector(
                "a.ld-sg-link[itemprop='telephone']"
            ).text.strip()
            info = {
                "url": link,
                "name": name,
                "address": street_address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "phone": phone,
            }
            store_info.append(info)
    return store_info


def get_page_url(location_name, urls):
    for row in urls:
        if row["name"] == location_name:
            return row["url"]
    return "https://www.londondrugs.com/store-locations/?context=storeLocator"


def fetch_data():
    urls = fetch_store_urls()
    driver = pull_content(API_URL)
    store_info = json.loads(driver.find_element_by_css_selector("pre").text)
    locations = []
    for row in store_info:
        location_name = handle_missing(row["name"])
        page_url = get_page_url(location_name, urls)
        street_address = handle_missing(row["address1"])
        city = handle_missing(row["city"])
        state = handle_missing(row["stateCode"])
        zip_code = handle_missing(row["postalCode"])
        phone = handle_missing(row["phone"])
        latitude = handle_missing(row["latitude"])
        longitude = handle_missing(row["longitude"])
        hours_of_operation = get_hours(row["storeHours"])
        store_number = row["id"].replace("_", "")
        country_code = row["countryCode"]
        location_type = "<MISSING>"
        log.info("Append {} => {}".format(location_name, street_address))
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
    driver.quit()
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
