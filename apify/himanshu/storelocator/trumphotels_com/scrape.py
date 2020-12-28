import csv
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import time
import os
from selenium.webdriver import FirefoxOptions

opts = FirefoxOptions()
opts.add_argument("--headless")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    path = os.path.abspath("geckodriver")
    driver = webdriver.Firefox(executable_path=path, options=opts)
    base_url = "https://www.trumphotels.com"
    driver.get("https://www.trumphotels.com/")
    driver.implicitly_wait(3)
    soup = BeautifulSoup(driver.page_source, "lxml")
    for country in soup.find("div", {"id": "ourhotels"}).find_all(
        "div", {"class": "filterlist"}
    ):
        for location in country.find_all("a"):
            driver.get(base_url + location["href"])
            time.sleep(5)
            page_url = base_url + location["href"]
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            for script in location_soup.find_all(
                "script", {"type": "application/ld+json"}
            ):
                if "address" in script.text:
                    store_data = json.loads(script.text)
                    if store_data["address"]["addressCountry"] not in ("USA", "Canada"):
                        continue
                    name = location.text.strip()
                    address = store_data["address"]
                    geo_location = location_soup.find("div", {"class": "map-outer-div"})
                    store = []
                    store.append("https://www.trumphotels.com")
                    store.append(name.replace("®", ""))
                    store.append(address["streetAddress"])
                    store.append(address["addressLocality"].split(",")[0])
                    store.append(
                        address["addressRegion"]
                        if "addressRegion" in address
                        else address["addressLocality"].split(",")[1]
                    )
                    store.append(address["postalCode"])
                    store.append("US" if address["addressCountry"] == "USA" else "CA")
                    store.append("<MISSING>")
                    store.append(
                        store_data["telephone"]
                        if store_data["telephone"]
                        else "<MISSING>"
                    )
                    store.append("<MISSING>")
                    store.append(geo_location["data-latitude"])
                    store.append(geo_location["data-longitude"])
                    store.append("<MISSING>")
                    store.append(page_url)
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
