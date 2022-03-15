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

    base_link = "https://aromajoes.com/who-we-are/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="c-tiles__item")
    locator_domain = "aromajoes.com"

    stores = json.loads(base.find(class_="c-locations__map-inner")["data-locations"])

    for i, item in enumerate(items):
        if "COMING SOON" in item.text.upper():
            continue
        location_name = item.find(class_="c-tiles__item-title").text.strip()
        raw_address = list(item.find(class_="c-tiles__item-text2").stripped_strings)
        try:
            city_line = raw_address[1].split(",")
            street_address = raw_address[0].replace("Assembly Row,", "").strip()
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
        except:
            city_line = raw_address[0].split(",")
            street_address = (
                stores[i]["location_address"]["address"].split(",")[0].strip()
            )
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        try:
            zip_code = city_line[-1].strip().split()[1].strip()
        except:
            try:
                zip_code = stores[i]["post_code"]
            except:
                zip_code = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "Open"
        phone = stores[i]["phone"]
        if "Comin" in phone:
            phone = "<MISSING>"
        hours_of_operation = (
            item.find(class_="c-tiles__item-text")
            .text.replace("\xa0", "")
            .replace("\n", " ")
            .replace("day:", "day ")
            .replace("  ", " ")
            .replace("NOW OPEN", "")
            .replace("!", "")
            .replace("Cafe", "")
            .strip()
        )
        if "Temporarily" in hours_of_operation:
            location_type = "Temp" + hours_of_operation.split("Temp")[1].strip()
            hours_of_operation = hours_of_operation.split("Temp")[0].strip()
        latitude = stores[i]["location_address"]["lat"]
        longitude = stores[i]["location_address"]["lng"]

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
