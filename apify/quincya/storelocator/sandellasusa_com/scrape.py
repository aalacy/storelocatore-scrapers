import csv
import re

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

    base_link = "https://sandellasusa.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found = []
    stores = []
    locator_domain = "sandellasusa.com"

    items = base.find_all("div", attrs={"data-ux": "ContentText"})

    for item in items:
        new_store = True
        lines = item.find_all("p")
        for line in lines:
            if new_store:
                store = []
                new_store = False
            item_text = " ".join(list(line.stripped_strings))
            if len(item_text.strip()) > 2:
                store.append(item_text)
            else:
                stores.append(store)
                new_store = True
        stores.append(store)

    for store in stores:
        if len(store) > 0:
            location_name = store[0]

            last = -1
            street_address = " ".join(store[1 : last - 1])
            if "-" in store[last] and "," in store[last]:
                store = store[last].replace("Ave Farm", "Ave|Farm").replace("\xa0", "")
                store = store[: store.rfind(" ")] + "|" + store[store.rfind(" ") + 1 :]
                store = store.split("|")
                street_address = store[0]
            elif "-" in store[last] or "." in store[last]:
                phone = store[last]
                city_line = (
                    store[last - 1]
                    .replace("Fargo ND", "Fargo, ND")
                    .replace("Newport RI", "Newport, RI")
                    .split(",")
                )
            elif ", " in store[last]:
                phone = "<MISSING>"
                city_line = store[last].split(",")
                street_address = " ".join(store[1:last])

            city = city_line[0].strip()
            state = city_line[1].split()[0].strip()
            zip_code = city_line[-1][-6:].replace("I ", "0").strip()

            if "Plaza M" in street_address:
                street_address = street_address.split("Plaza")[1].strip()
            else:
                try:
                    digit = re.search(r"\d", street_address).start(0)
                    if digit != 0:
                        street_address = street_address[digit:]
                except:
                    pass

            if location_name + street_address in found:
                continue
            found.append(location_name + street_address)

            country_code = "US"

            store_number = (
                location_type
            ) = hours_of_operation = latitude = longitude = "<MISSING>"

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
