import csv
import re
import time

from bs4 import BeautifulSoup

from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_url = "https://www.muchasgraciasmexicanfood.com/locations/"

    driver = SgChrome().driver()

    driver.get(base_url)
    time.sleep(8)

    base = BeautifulSoup(driver.page_source, "lxml")

    return_main_object = []

    items = base.find_all(class_="sl-item")

    for i, location_soup in enumerate(items):
        location_name = location_soup.find(class_="p-title").text.strip()
        addr = list(location_soup.find(class_="p-area").stripped_strings)
        street_address = addr[0].strip()
        city_line = addr[1].split(",")
        city = city_line[0].strip()
        state = city_line[1].strip()
        zipp = city_line[2].strip()

        try:
            phone = re.findall(r"\([\d]{3}\) [\d]{3}-[\d]{4}", location_soup.text)[0]
        except:
            phone = "<MISSING>"

        days = ""
        hours = ""
        ps = location_soup.find_all(class_="p-area")
        for p in ps:
            if "mon," in p.text.lower():
                days = p.text
            if ":00 " in p.text.lower():
                hours = p.text.strip()

        if days and hours:
            hours_of_operation = hours + days
        else:
            hours_of_operation = "<MISSING>"

        if "24 Hours" in location_soup.text:
            hours_of_operation = "Open 24 Hours"

        driver.find_elements_by_class_name("sl-item")[i].click()
        time.sleep(2)
        try:
            raw_gps = driver.find_element_by_xpath(
                "//*[(@title='Open this area in Google Maps (opens a new window)')]"
            ).get_attribute("href")
            latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
            longitude = raw_gps[raw_gps.find(",") + 1 : raw_gps.find("&")].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        store = []
        store.append("muchasgraciasmexicanfood.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(base_url)
        return_main_object.append(store)
    driver.close()
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
