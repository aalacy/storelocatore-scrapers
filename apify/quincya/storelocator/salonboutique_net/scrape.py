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

    base_link = "http://www.salonboutique.net/salon-boutique-luxury-rentals-2/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="heading icon-left")
    locator_domain = "salonboutique.net"

    for i in items:
        item = i.find_previous("div")
        try:
            link = item.a["href"]
        except:
            link = base_link

        location_name = item.h2.text.strip()

        try:
            raw_data = list(item.p.stripped_strings)
        except:
            raw_data = list(item.find_all("div")[2].stripped_strings)
        if "Manager" in raw_data[0]:
            raw_data.pop(0)
        if "Shannon Salz" in raw_data[0]:
            raw_data.pop(0)
        street_address = raw_data[0].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city_line = raw_data[1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_data[2]
        if ":" in phone:
            phone = phone.split(":")[1].strip()
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if link != base_link:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                latitude = re.findall(r'latitude":[0-9]{2}\.[0-9]+', str(base))[
                    0
                ].split(":")[1][:10]
                longitude = re.findall(r'longitude":-[0-9]{2,3}\.[0-9]+', str(base),)[
                    0
                ].split(":")[1][:12]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

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
