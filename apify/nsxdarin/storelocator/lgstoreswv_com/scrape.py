import csv
import re

from bs4 import BeautifulSoup

from sgselenium import SgSelenium

driver = SgSelenium().chrome()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://lgstoreswv.com/locations/"
    driver.get(url)
    base = BeautifulSoup(driver.page_source, "lxml")

    data = []
    found = []
    website = "lgstoreswv.com"
    country = "US"
    hours = "<MISSING>"

    items = base.find_all(class_="owl-item")
    for item in items:
        if "data-address" in str(item):
            name = item.find(class_="wpgmza_carousel_info_holder").find_all("p")[1].text
            if name in found:
                continue
            found.append(name)
            store = name.split("#")[1].strip()
            addinfo = (
                item.find(class_="wpgmza_carousel_info_holder")
                .find_all("p")[2]
                .text.replace("Avenue, SW", "Avenue SW")
                .replace("Rd - Hunting", "Rd, Hunting")
            )
            add = addinfo.split(",")[0]
            city = addinfo.split(",")[1].strip()
            state = addinfo.split(",")[-1][:-5].strip()
            zc = addinfo.rsplit(" ", 1)[1]
            phone = (
                item.find(class_="wpgmza_carousel_info_holder")
                .find_all("p")[-3]
                .text.strip()
            )
            if "," in phone:
                try:
                    phone = re.findall("[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
                except:
                    phone = "<MISSING>"
            typ = item.img["src"].split("/")[-1].split("-MapIcon")[0].strip()
            lat = item.div["data-latlng"].split(",")[0].strip()
            lng = item.div["data-latlng"].split(",")[1].strip()
            purl = "https://lgstoreswv.com/locations/"

            data.append(
                [
                    website,
                    purl,
                    name,
                    add,
                    city,
                    state,
                    zc,
                    country,
                    store,
                    phone,
                    typ,
                    lat,
                    lng,
                    hours,
                ]
            )
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
