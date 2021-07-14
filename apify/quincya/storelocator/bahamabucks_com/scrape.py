import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://bahamabucks.com/locations/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.script.contents[0].split("shops:")[1].split("}\n}")[0] + "}}"
    stores = json.loads(js)

    items = base.find_all(class_="location-result")

    data = []
    locator_domain = "bahamabucks.com"

    for store_number in stores:
        store = stores[store_number]
        location_name = store["information"]["shop_location"]
        street_address = (
            store["address"]["line1"].strip() + " " + store["address"]["line2"].strip()
        )
        city = store["address"]["city"]
        state = store["address"]["state"]
        zip_code = store["address"]["zip"]
        country_code = "US"
        location_type = "<MISSING>"
        phone = store["information"]["phone"]
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = ""
        try:
            raw_hours = store["hours"]["current_hours"]
            for day in raw_hours:
                if "day" in day:
                    hours_of_operation = (
                        hours_of_operation + " " + day.title() + " " + raw_hours[day]
                    ).strip()
        except:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.count("Game Days") == 7:
            hours_of_operation = "<MISSING>"
        latitude = store["address"]["latitude"]
        longitude = store["address"]["longitude"]

        for item in items:
            if item["id"].split("-")[1] == store_number:
                link = "https://bahamabucks.com" + item.a["href"].replace(
                    "bayamón", "bayamon"
                )

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
