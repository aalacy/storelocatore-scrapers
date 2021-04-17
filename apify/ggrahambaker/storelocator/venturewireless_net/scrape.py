import csv

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


def addy_ext(addy):
    addy = addy.split(",")
    city = addy[0]
    state_zip = " ".join(addy[1].split()).split(" ")
    state = state_zip[0].strip()
    zip_code = state_zip[1].strip()
    return city, state, zip_code


def fetch_data():

    base_link = "https://www.venturewireless.net/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "venturewireless.net"

    conts = base.find_all(class_="_1Z_nJ")
    all_store_data = []
    for cont in conts:
        info = list(cont.stripped_strings)
        if len(info) < 2:
            continue

        location_name = info[0]
        street_address = info[1].replace("\xa0", "").strip()
        city, state, zip_code = addy_ext(info[2].replace("\xa0", ""))
        phone_number = info[3]

        hours = ""
        for h in info[5:]:
            hours += h + " "

        hours = hours.replace("\xa0", "").strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        lat = "<INACCESSIBLE>"
        longit = "<INACCESSIBLE>"
        page_url = "https://www.venturewireless.net/locations"
        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]

        all_store_data.append(store_data)
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
