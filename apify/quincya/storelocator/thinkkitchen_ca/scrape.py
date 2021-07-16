import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    locator_domain = "stokesstores.com"

    base_link = "https://www.stokesstores.com/en/storelocator/"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    fin_script = ""
    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "storelocator_id" in str(script):
            fin_script = str(script)
            break

    stores = json.loads(fin_script.split("stores ")[1].split(",\n")[0].strip()[1:])

    for store in stores:
        location_name = store["name"]
        street_address = store["address"].replace("\x92", " ").split("(")[0].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zipcode"]
        country_code = store["country"]
        store_number = store["storelocator_id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        latitude = store["latitude"]
        try:
            longitude = store["longitude"]
        except:
            longitude = store["longtitude"]
        link = "https://www.stokesstores.com/en/" + store[
            "rewrite_request_path"
        ].replace("`", "")

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = " ".join(
            list(base.find(class_="opening-hours").table.stripped_strings)
        )

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
