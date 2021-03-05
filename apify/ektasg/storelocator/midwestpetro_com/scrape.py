import csv
import re
import time

from sglogging import SgLogSetup

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("midwestpetro_com")


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


def parse_geo(url):
    try:
        lon = re.findall(r"\,(--?[\d\.]*)", url)[0]
    except:
        lon = url.split("/@")[1].split(",")[1].split(",")[0]
    lat = re.findall(r"\@(-?[\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data = []
    count = 0

    driver = SgChrome().chrome()

    driver.get("https://midwestpetro.com/#locations?all")
    time.sleep(5)
    stores = driver.find_elements_by_css_selector("div.search-row")
    page_url = "https://midwestpetro.com/#locations?all"
    for store in stores:
        location_name = store.find_element_by_id("station-name").text
        store_num = location_name.split("#")[1]
        phone = store.find_element_by_css_selector(
            "div.search-result-link.right"
        ).text.splitlines()[1]
        loc_type = store.find_element_by_id("brand_logo").get_attribute("alt")
        addr = store.find_element_by_css_selector(
            "div.search-result.four"
        ).text.splitlines()
        street_addr = addr[0]
        zipcode = addr[1].split(" ")[-1]
        state = addr[1].split(" ")[-2]
        city_list = addr[1].split(" ")[0:-2]
        if len(city_list) == 1:
            city = city_list[0]
        else:
            city = city_list[0] + " " + city_list[1]
        hours_of_op = store.find_element_by_css_selector("div.search-result.two").text
        if hours_of_op == "":
            hours_of_op = store.find_element_by_css_selector(
                "div.search-result.two > img"
            ).get_attribute("alt")
        data.append(
            [
                "https://www.midwestpetro.com/",
                page_url,
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                "US",
                store_num,
                phone,
                loc_type,
                "<MISSING>",
                "<MISSING>",
                hours_of_op,
            ]
        )
        count += 1
        logger.info(count)

    time.sleep(3)
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
