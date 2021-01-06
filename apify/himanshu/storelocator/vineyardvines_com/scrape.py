import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    r = session.get("https://www.vineyardvines.com/stores", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []

    locations = soup.find(id="allstores").find_all(class_="store store-card")
    for location in locations:
        if "/storedetails?StoreID=" not in location.a["href"]:
            continue
        link = "https://www.vineyardvines.com" + location.a["href"]
        location_request = session.get(link, headers=headers)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        name = location_soup.find("h2", {"class": "storedetail_name"}).text
        phone = (
            location_soup.find("p", {"itemprop": "telephone"})
            .find("a")["href"]
            .split("tel:")[1]
            .replace("\u200b", "")
        )
        address = list(
            location_soup.find("ul", {"class": "storedetail_address"}).stripped_strings
        )
        store_hours = location_soup.find_all("span", {"itemprop": "openingHours"})
        hours = ""
        for i in range(len(store_hours)):
            hours = hours + " ".join(list(store_hours[i].stripped_strings)) + " "
        if "closed until further notice" in location_soup.text:
            hours = "Closed until further notice"
        if not hours:
            hours = "<MISSING>"
        store = []
        store.append("https://www.vineyardvines.com")
        store.append(name)
        street = (
            location_soup.find("ul", {"class": "storedetail_address"})
            .li.text.replace("\n", " ")
            .replace("Carmel Plaza  ,", "")
            .replace("  , ", ", ")
            .strip()
        )

        if "airport" not in name.lower() and "Ocean Ave" not in street:
            try:
                digit = re.search(r"\d", street).start(0)
                if digit != 0:
                    street = street[digit:]
            except:
                pass

        store.append(street)
        store.append(address[-1].split(",")[0])
        if len(address[-1].split(",")[1].split(" ")) < 3:
            store.append(address[-1].split(",")[1].split(" ")[-1])
            store.append("<MISSING>")
        else:
            store.append(address[-1].split(",")[1].split(" ")[-2])
            store.append(address[-1].split(",")[1].split(" ")[-1])
        if len(store[-1]) < 5:
            continue
        store.append("US")
        store.append(location.a["href"].split("=")[1])
        store.append(phone if phone != "null" else "<MISSING>")
        store.append("<MISSING>")
        lat = (
            location_soup.find("a", {"id": "getdirections"})["href"]
            .split("&sll=")[1]
            .split(",")[0]
            .strip()
        )
        lng = (
            location_soup.find("a", {"id": "getdirections"})["href"]
            .split("&sll=")[1]
            .split(",")[1]
            .split("&")[0]
            .strip()
        )
        if "7000 Arundel" in street:
            lat = "39.157299"
            lng = "-76.72557"
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(link)
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
