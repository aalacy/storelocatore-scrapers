import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://www.mfaoil.com/store-locator-data/?brands=&searchfilters=&lat=37.9642529&lng=-91.8318334&maxdist=10000"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = json.loads(base.text.strip())

    data = []
    locator_domain = "mfaoil.com"

    for store in stores:
        location_name = store["location_name"].strip()
        link = store["url"]
        if "/store/" in link:
            link = "https://www.mfaoil.com" + link
        street_address = store["address"].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zipCode"]
        country_code = "US"
        store_number = store["id"]
        phone = store["phone"]
        if not phone:
            phone = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        location_type = "<MISSING>"

        if "mfaoil.com" in link:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            hours_of_operation = ""
            try:
                hours_of_operation = base.find(class_="fueling").text.strip()
            except:
                pass
            try:
                raw_hours = (
                    base.find(class_="hours")
                    .text.strip()
                    .replace("\n\n\n", " ")
                    .replace("\n", " ")
                )
                hours_of_operation = hours_of_operation + " " + raw_hours
            except:
                pass
            try:
                location_type = (
                    base.find(class_="aminities")
                    .text.strip()
                    .replace("\t", "")
                    .replace("\r\n", ",")
                    .replace("\n", "")
                    .strip()
                )
            except:
                pass
        else:
            continue

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        # Store data
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

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
