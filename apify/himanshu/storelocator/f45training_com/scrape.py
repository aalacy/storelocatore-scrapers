import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup
from geopy.geocoders import Nominatim

logger = SgLogSetup().get_logger("f45training_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    base_url = "https://f45training.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36"
    }
    for index, url in enumerate(
        [
            "https://f45training.com/find-a-studio/",
            "https://f45training.ca/find-a-studio/",
        ]
    ):
        if index == 0:
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            data = soup.find("div", {"class": "clear-fix"}).find_all("li")

            for dt in data:
                page_url = dt.find("a")["href"]
                location_name = (
                    dt.find("span", {"class": "text-wrapper"})
                    .text.strip()
                    .replace("F45", "")
                    .replace("  – Opening Soon", " – Opening Soon")
                )

                r1 = session.get(page_url, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                try:
                    all_data = (
                        soup1.find("div", {"class": "sm-ptb"}).find("p").text.split(",")
                    )
                except:
                    pass
                try:
                    temp_latitude = (
                        soup1.find("div", {"class": "sm-ptb"})
                        .find("a")["href"]
                        .split("=")[1]
                        .split(",")
                    )
                    latitude = temp_latitude[0]
                except:
                    latitude = "<MISSING>"
                try:
                    temp_longitude = (
                        soup1.find("div", {"class": "sm-ptb"})
                        .find("a")["href"]
                        .split("=")[1]
                        .split(",")
                    )
                    longitude = temp_longitude[1]
                except:
                    longitude = "<MISSING>"
                try:
                    street_address = all_data[0]
                except:
                    street_address = "<MISSING>"
                try:
                    temp_data = (
                        soup1.find("div", {"class": "sm-ptb"})
                        .find("a")["href"]
                        .split("=")[1]
                        .split(",")
                    )
                    geolocator = Nominatim(user_agent="myApp")
                    location = geolocator.reverse(temp_data)
                    i = location.raw["address"]
                except:
                    continue
                try:
                    city = i["city"]
                except:
                    city = "<MISSING>"
                try:
                    try:
                        all_data = soup1.find("div", {"class": "sm-ptb"}).find("p").text
                        a = re.findall("[A-Z]{2}", all_data)
                        state = a[0]
                        if "US" in state:
                            state = "<MISSING>"
                        else:
                            state = a[0]
                    except:
                        state = "<MISSING>"
                except:
                    state = "<MISSING>"
                try:
                    all_data = soup1.find("div", {"class": "sm-ptb"}).find("p").text
                    post_code = re.findall(r"\d{5}(?:[-\s]\d{4})?", all_data)
                    try:
                        c = post_code[0]
                        if len(c) == 5:
                            zipp = c
                    except:
                        zipp = "<MISSING>"
                except:
                    zipp = "<MISSING>"

                country_code = "US"
                store_number = "<MISSING>"

                try:
                    phone = (
                        soup1.find("a", {"href": re.compile("tel:")})
                        .text.split("/")[0]
                        .split(",")[0]
                        .replace("(JF45)", "")
                    )
                except:
                    phone = "<MISSING>"
                try:
                    location_type = "F45 Training"
                except:
                    location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"
                street_address = (
                    street_address.replace(city, "")
                    .replace(state, "")
                    .replace(zipp, "")
                    .strip()
                )
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type)
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation)
                store.append(page_url if page_url else "<MISSING>")
                store = [
                    x.strip().replace("\n", " ").replace("\t", "").replace("\r", "")
                    if isinstance(x, str)
                    else x
                    for x in store
                ]
                yield store

        elif index == 1:
            r2 = session.get(url, headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            data1 = soup2.find("div", {"class": "clear-fix"}).find_all("li")

            for dt1 in data1:
                page_url = dt1.find("a")["href"]
                location_name = (
                    dt1.find("span", {"class": "text-wrapper"})
                    .text.strip()
                    .replace("F45", "")
                    .replace(
                        "                                                                 – Opening Soon",
                        " – Opening Soon",
                    )
                )
                r3 = session.get(page_url, headers=headers)
                soup3 = BeautifulSoup(r3.text, "lxml")
                try:
                    all_data = (
                        soup3.find("div", {"class": "sm-ptb"}).find("p").text.split(",")
                    )
                except:
                    pass
                try:
                    street_address = all_data[0]
                except:
                    street_address = "<MISSING>"
                try:
                    temp_latitude1 = (
                        soup3.find("div", {"class": "sm-ptb"})
                        .find("a")["href"]
                        .split("=")[1]
                        .split(",")
                    )
                    latitude = temp_latitude1[0]
                except:
                    latitude = "<MISSING>"
                try:
                    temp_longitude1 = (
                        soup3.find("div", {"class": "sm-ptb"})
                        .find("a")["href"]
                        .split("=")[1]
                        .split(",")
                    )
                    longitude = temp_longitude1[1]
                except:
                    longitude = "<MISSING>"
                try:
                    temp_data1 = (
                        soup3.find("div", {"class": "sm-ptb"})
                        .find("a")["href"]
                        .split("=")[1]
                        .split(",")
                    )
                    geolocator = Nominatim(user_agent="myApp")
                    location1 = geolocator.reverse(temp_data1)
                    j = location1.raw["address"]
                except:
                    continue
                try:
                    city = j["city"]
                except:
                    city = "<MISSING>"
                try:
                    try:
                        all_data = soup1.find("div", {"class": "sm-ptb"}).find("p").text
                        b = re.findall("[A-Z]{2}", all_data)
                        state = b[0]
                    except:
                        state = "<MISSING>"
                except:
                    state = "<MISSING>"
                try:
                    all_data = soup3.find("div", {"class": "sm-ptb"}).find("p").text
                    post = re.findall(
                        r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}", all_data
                    )
                    try:
                        d = post[0]
                        if len(d) == 7:
                            zipp = d
                    except:
                        zipp = "<MISSING>"
                except:
                    zipp = "<MISSING>"
                country_code = "CA"
                store_number = "<MISSING>"
                try:
                    phone = (
                        soup3.find("a", {"href": re.compile("tel:")})
                        .text.split("/")[0]
                        .split(",")[0]
                        .replace("(JF45)", "")
                    )
                except:
                    phone = "<MISSING>"
                try:
                    location_type = "F45 Training"
                except:
                    location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"

                street_address = (
                    street_address.replace(city, "")
                    .replace(state, "")
                    .replace(zipp, "")
                    .strip()
                )
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type)
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation)
                store.append(page_url if page_url else "<MISSING>")
                store = [
                    x.strip().replace("\n", " ").replace("\t", "").replace("\r", "")
                    if isinstance(x, str)
                    else x
                    for x in store
                ]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
