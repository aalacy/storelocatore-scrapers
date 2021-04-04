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

    base_link = "https://www.chromehearts.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = items = base.find(class_="v-locations__data-simple").find_all("li")
    locator_domain = "chromehearts.com"

    for item in items:

        location_name = item.strong.text

        raw_address = str(item.find(class_="address-link"))[:-4].replace("<br/>", ",")
        raw_address = raw_address[raw_address.rfind(">") + 1 :].split(",")

        try:
            street_address = raw_address[-4].strip() + " " + raw_address[-3].strip()
        except:
            street_address = raw_address[-3].strip()
        street_address = street_address.replace("\n", " ").replace("\r", " ")
        street_address = (re.sub(" +", " ", street_address)).strip()
        if street_address == "Gustavia":
            continue
        city = raw_address[-2].strip()
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find(class_="phone").text.replace("Tel:", "").strip()

        hours_of_operation = "<MISSING>"

        try:
            map_link = item.a["href"]
            at_pos = map_link.rfind("@")
            latitude = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
            longitude = map_link[
                map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
            ].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if not latitude[-3:].isdigit():
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
