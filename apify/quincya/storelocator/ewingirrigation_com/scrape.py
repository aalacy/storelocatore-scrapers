import csv
import re

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

    base_link = "https://store.ewingirrigation.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="storeslist").find_all(class_="liststores")

    data = []

    for item in items:

        locator_domain = "ewingirrigation.com"
        location_name = "Ewing " + item.find(class_="store_content").a.text.strip()

        raw_address = (
            item.find(class_="address")
            .text.replace(" CO 80", " CO, 80")
            .replace("\r\n\r\n", "\n")
            .split("\n")
        )
        street_address = raw_address[0].strip()
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[1].strip()
        zip_code = city_line[2].strip()
        if len(zip_code) > 5:
            if "-" not in zip_code:
                zip_code = zip_code[:5] + "-" + zip_code[5:]
        country_code = "US"

        store_number = item.find(class_="number").text.strip()
        try:
            phone = item.find(class_="phone").text.strip()
        except:
            phone = "<MISSING>"

        location_type = "<MISSING>"

        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(item))[0].split(
            ","
        )
        latitude = geo[0]
        longitude = geo[1]
        if longitude == "-111.9":
            longitude = "-111.9000"

        hours = (
            " ".join(list(item.find(class_="opening_hours_block").stripped_strings))
            .replace("\xa0", "")
            .replace("\n", " ")
            .replace("AM", "AM ")
            .replace("day", "day ")
            .strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours)).strip()

        link = item.a["data-url"]

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
