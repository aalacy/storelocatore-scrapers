import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

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


def fetch_data():

    session = SgRequests()

    base_link = "https://www.amigosunited.com/rs/StoreLocator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")

    data = []
    locator_domain = "amigosunited.com"

    items = base.find_all(class_="storeresult-listitem col-sm-12")

    for item in items:

        raw_address = list(item.find(class_="store-address").stripped_strings)
        street_address = raw_address[0].strip()
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[1].strip().split()[0]
        zip_code = city_line[1].strip().split()[1]
        country_code = "US"
        location_name = "Amigos " + city
        phone = item.find(class_="store-phone").text.strip()
        store_number = item["id"].split("-")[-1]
        hours_of_operation = item.find(class_="store-hours").text.strip()
        location_type = "<MISSING>"

        link = (
            "https://www.amigosunited.com"
            + item.find("a", string="Store Details")["href"]
        )

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        types = base.find_all(class_="col-xs-12 col-sm-6 col-md-3")
        for raw in types:
            if "store features" in raw.text.lower():
                location_type = (
                    ", ".join(list(raw.stripped_strings)).split("eatures,")[1].strip()
                )
                break
        latitude = re.findall(r":[0-9]{2}\.[0-9]+", str(base))[0][1:]
        longitude = re.findall(r":-[0-9]{2,3}\.[0-9]+", str(base))[0][1:]

        data.append(
            [
                locator_domain,
                link,
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
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
