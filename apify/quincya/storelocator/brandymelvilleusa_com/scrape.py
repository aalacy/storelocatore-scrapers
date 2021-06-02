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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://locations.brandymelville.com/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    locator_domain = "brandymelville.com"

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "locations = {" in str(script):
            script = str(script)
            break

    locator_domain = "menards.com"

    js = script.split('data":')[1].split("};\n\n")[0].strip()
    items = json.loads(js)

    for i in items:
        if i in ["United States", "United Kingdom", "Canada"]:
            country_code = i
            states = items[i]

            for state in states:
                stores = states[state]

                for store in stores:
                    street_address = store[1]
                    city = store[0]
                    state = state.replace("Washington", "WA")
                    location_name = "Brandy Melville - " + city
                    zip_code = "<MISSING>"
                    phone = store[2]
                    hours_of_operation = store[4]
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    store_number = "<MISSING>"
                    location_type = "<MISSING>"
                    if city == "London":
                        state = "<MISSING>"
                    if not phone:
                        phone = "<MISSING>"

                    if "Kingdom" not in country_code:
                        digit = re.search(r"\d", street_address).start(0)
                        if digit != 0:
                            street_address = street_address[digit:]

                    # Store data
                    data.append(
                        [
                            locator_domain,
                            base_link,
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
