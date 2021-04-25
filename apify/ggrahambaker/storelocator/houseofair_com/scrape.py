import csv
from sgselenium import SgSelenium
import usaddress
import re
import json
from sglogging import sglog

DOMAIN = "houseofair.com"
BASE_URL = "https://www.houseofair.com"
LOCATION_URL = "https://www.houseofair.com/locations"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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


def parse_addy(addy):
    parsed_add = usaddress.tag(addy)[0]

    street_address = ""

    if "AddressNumber" in parsed_add:
        street_address += parsed_add["AddressNumber"] + " "
    if "StreetNamePreDirectional" in parsed_add:
        street_address += parsed_add["StreetNamePreDirectional"] + " "
    if "StreetNamePreType" in parsed_add:
        street_address += parsed_add["StreetNamePreType"] + " "
    if "StreetName" in parsed_add:
        street_address += parsed_add["StreetName"] + " "
    if "StreetNamePostType" in parsed_add:
        street_address += parsed_add["StreetNamePostType"] + " "
    if "OccupancyType" in parsed_add:
        street_address += parsed_add["OccupancyType"] + " "
    if "OccupancyIdentifier" in parsed_add:
        street_address += parsed_add["OccupancyIdentifier"] + " "

    street_address = street_address.strip()
    city = parsed_add["PlaceName"].strip()
    state = parsed_add["StateName"].strip()
    zip_code = parsed_add["ZipCode"].strip()

    return street_address, city, state, zip_code


def parse_json(driver):
    info = driver.find_elements_by_css_selector("script[type='application/ld+json']")[
        1
    ].get_attribute("innerHTML")
    data = json.loads(info)
    return data


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)

    main = driver.find_element_by_css_selector("section#content-locations")
    locs = main.find_elements_by_css_selector("div.col-md-3")
    link_list = []
    for loc in locs:
        link = loc.find_element_by_css_selector("a").get_attribute("href")
        if ".pl/" in link:
            continue
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        page_url = link + "trampoline-park/"
        log.info("Pull content => " + page_url)
        driver.get(page_url)
        details = parse_json(driver)
        check_closed = driver.find_elements_by_xpath(
            "//span[contains(@class, 'label-danger') and contains(text(), 'Temporarily Closed')]"
        )
        if len(check_closed) > 0:
            hours = "TEMP_CLOSED"
        else:
            hours_ul = driver.find_element_by_xpath(
                "//h3[contains(text(),'General Access')]/following-sibling::ul | //h3[contains(text(),'Hours of Operation')]/following-sibling::ul"
            )
            hours = hours_ul.text.replace("\n", ",").strip()
            hours = re.sub(",$", "", re.sub("Phone Hours.*", "", hours))

        location_name = details["name"]
        street_address = details["address"]["streetAddress"]
        city = details["address"]["addressLocality"]
        state = details["address"]["addressRegion"]
        zip_code = details["address"]["postalCode"]
        country_code = details["address"]["addressCountry"]
        lat = details["geo"]["latitude"]
        lng = details["geo"]["longitude"]
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        phone_number = details["telephone"]

        store_data = [
            DOMAIN,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            lng,
            hours,
        ]
        log.info("Append {} => {}".format(location_name, street_address))
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
