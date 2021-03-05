import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import phonenumbers
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("worldgym_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://www.worldgym.com/findagym"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    json_data = json.loads(
        str(soup).split("franhiseeLocations=")[1].split(';$(".header')[0]
    )

    for data in json_data:
        country_code = data["Country"].replace("USA", "US").replace("Canada", "CA")
        if country_code not in ["US", "CA"]:
            continue

        location_name = data["LocationName"]
        street_address = (data["Line1"] + " " + str(data["Line2"])).strip()
        city = data["City"]
        state = data["State"].replace("QB", "QC")
        zipp = data["Postal"]
        store_number = "<MISSING>"
        if data["PhoneWithOutCountryCode"]:
            phone = phonenumbers.format_number(
                phonenumbers.parse(str(data["PhoneWithOutCountryCode"]), "US"),
                phonenumbers.PhoneNumberFormat.NATIONAL,
            )
        else:
            phone = "<MISSING>"
        location_type = "Gym"
        latitude = data["Latitude"]
        longitude = data["Longitude"]
        page_url = data["MicroSiteUrl"]

        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if (
            "Time to get fit..."
            in soup1.find("div", {"class": "tab-pane gymhourstab"}).text
        ):
            hours_of_operation = " ".join(
                list(
                    soup1.find(
                        "div", {"class": "tab-pane gymhourstab"}
                    ).stripped_strings
                )
            ).replace("Time to get fit... Hours", "")
        else:
            hours_of_operation = soup1.find(
                "h5", {"class": "readmore text-center"}
            ).text.strip()

        store = []
        store.append("https://worldgym.com/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
