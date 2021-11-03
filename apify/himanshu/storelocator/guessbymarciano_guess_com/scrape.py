import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    addressess = []
    base_url = "marciano.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    location_url = "https://stores.marciano.com/us/en/browse/"
    all_soup = BeautifulSoup(session.get(location_url, headers=headers).content, "lxml")
    for i in all_soup.find("div", {"class": "browse-mode-list"}).find_all(
        "li", {"class": "map-list-item-wrap is-single"}
    ):
        alink = i.find("div", {"class": "map-list-item is-single"}).find("a")["href"]
        city_soup = BeautifulSoup(session.get(alink).content, "lxml")
        for city_link in city_soup.find_all("a", {"title": re.compile("stores in")}):
            store_soup = BeautifulSoup(session.get(city_link["href"]).content, "lxml")
            for url in store_soup.find_all("a", {"title": re.compile("#")}):
                page_url = url["href"]
                location_soup = BeautifulSoup(session.get(page_url).content, "lxml")
                location_name = (
                    location_soup.find("div", {"class": "location-name-wrap flex"})
                    .find("h2")
                    .text
                )
                raw_addr = (
                    location_soup.find("p", {"class": "address ft-14 underline"})[
                        "aria-label"
                    ]
                    .replace("This location is located at ", "")
                    .split(",")
                )
                street_address = raw_addr[0].strip()
                city = raw_addr[1].strip()
                state = raw_addr[2].split(" ")[1]
                zipp = raw_addr[2].split(" ")[2]
                country_code = "US"
                store_number = "<MISSING>"
                phone = location_soup.find("a", {"title": "Call store"}).text
                location_type = "<MISSING>"
                raw_loc = (
                    location_soup.find("a", {"title": "Get directions"})["href"]
                    .split("=")[-1]
                    .split(",")
                )
                latitude = raw_loc[0]
                longitude = raw_loc[1]
                hours_of_operation = " ".join(
                    list(location_soup.find("div", {"class": "hours"}).stripped_strings)
                )
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(page_url)
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
