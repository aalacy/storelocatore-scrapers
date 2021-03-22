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


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():

    session = SgRequests()

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    locator_domain = "https://www.eatrockefeller.com/"

    link = "https://www.eatrockefeller.com/locations"

    req = session.get(link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="Containercf5y").div.div.find_all("section", recursive=False)[
        1:
    ]

    all_store_data = []
    for item in items:
        content = list(item.stripped_strings)

        if "OPENING" in content[0]:
            content.pop(0)

        if "Pickup" in content[0]:
            content.pop(0)

        if "Delivery" in content[0]:
            content.pop(0)

        location_name = content[0]
        phone_number = content[1]
        street_address = content[2]
        city, state, zip_code = addy_ext(content[3])
        hours = ""
        for h in content[4:]:
            hours += h + " "

        if "Hours" in hours:
            hours = hours[hours.find("Hours") + 6 :].replace(": Mo", "Mo").strip()
        hours = hours.split("Pickup")[0].strip()

        if "temporarily" in hours:
            hours = "Temporarily Closed"

        if street_address == "1209 Highland Avenue":
            lat = "33.885931"
            longit = "-118.410312"
        elif street_address == "418 Pier Avenue":
            lat = "33.864034"
            longit = "-118.397218"
        elif street_address == "1707 South Catalina Avenue":
            lat = "33.818388"
            longit = "-118.388446"
        else:
            lat = "<INACCESSIBLE>"
            longit = "<INACCESSIBLE>"

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        store_data = [
            locator_domain,
            link,
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
        ]
        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
